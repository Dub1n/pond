from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple

import yaml

from .flags import is_relationship_schema
from ..ifc import normalize_ifc_class, normalize_ifc_predefined_type, normalize_pset_name

AxisToken = str
PosToken = str
FrameToken = str

AXIS_ORDER = {"x": 0, "y": 1, "z": 2}
VALID_FRAMES = {"world", "local"}
CENTER_PREFIXES = {"c", "~"}


class SchemaError(ValueError):
    """Raised when a relationship-first schema document is invalid."""


# --------------------------------------------------------------------------- #
# Dimension handling


def _normalise_mapping(data: Mapping[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in data.items():
        str_key = str(key)
        if isinstance(value, Mapping):
            result[str_key] = _normalise_mapping(value)
        else:
            result[str_key] = value
    return result


class DimensionResolver:
    """
    Resolves dotted dimension references (e.g. `structure.backspan`) and
    lightweight expressions against a nested dimension mapping.
    """

    def __init__(self, raw: Mapping[str, Any]) -> None:
        self.raw: Dict[str, Any] = _normalise_mapping(raw)
        self._values: Dict[str, float] = {}
        self._resolving: set[str] = set()
        self._aliases: Dict[str, Optional[str]] = {}
        self._register_aliases(self.raw)
        self._resolve_all()

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any] | None) -> "DimensionResolver":
        mapping = mapping or {}
        if not isinstance(mapping, Mapping):
            raise SchemaError("dimensions must be a mapping when provided")
        return cls(mapping)

    def _register_aliases(self, mapping: Mapping[str, Any], prefix: str = "") -> None:
        for key, value in mapping.items():
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(value, Mapping):
                self._register_aliases(value, path)
            else:
                if key not in self._aliases:
                    self._aliases[key] = path
                    continue
                existing = self._aliases[key]
                if existing is None:
                    continue
                if existing != path:
                    self._aliases[key] = None

    def _resolve_all(self) -> None:
        for dotted_path in list(self._iter_paths(self.raw)):
            self.resolve_path(dotted_path)

    def _iter_paths(self, mapping: Mapping[str, Any], prefix: str = "") -> Iterable[str]:
        for key, value in mapping.items():
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(value, Mapping):
                yield from self._iter_paths(value, path)
            else:
                yield path

    def resolve_path(self, dotted: str) -> float:
        dotted = dotted.strip()
        if dotted.startswith("dimensions."):
            dotted = dotted[len("dimensions.") :]
        if dotted in self._values:
            return self._values[dotted]
        if dotted in self._resolving:
            raise SchemaError(f"dimensions contain a circular reference at '{dotted}'")
        self._resolving.add(dotted)
        raw_value = self._lookup_raw(dotted)
        resolved = self._resolve_value(raw_value)
        self._values[dotted] = resolved
        leaf = dotted.split(".")[-1]
        if self._aliases.get(leaf) == dotted and leaf not in self._values:
            self._values[leaf] = resolved
        self._resolving.remove(dotted)
        return resolved

    def _lookup_raw(self, dotted: str) -> Any:
        parts = dotted.split(".")
        cursor: Any = self.raw
        for part in parts:
            if not isinstance(cursor, Mapping) or part not in cursor:
                raise SchemaError(f"dimension '{dotted}' is not defined")
            cursor = cursor[part]
        return cursor

    def evaluate(self, expr: str) -> float:
        try:
            node = ast.parse(expr, mode="eval")
        except SyntaxError as exc:
            raise SchemaError(f"invalid expression '{expr}': {exc}") from exc
        return self._eval_ast(node.body)

    def lookup(self, name: str) -> float:
        name = name.strip()
        if name.startswith("dimensions."):
            name = name[len("dimensions.") :]
        if name in self._values:
            return self._values[name]
        alias = self._aliases.get(name)
        if alias:
            return self.resolve_path(alias)
        return self.resolve_path(name)

    def _resolve_value(self, value: Any) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return self.evaluate(value)
        raise SchemaError(f"dimensions must be numeric or expressions, got {value!r}")

    def _eval_ast(self, node: ast.AST) -> float:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise SchemaError(f"unsupported literal {node.value!r} in expression")
        if isinstance(node, ast.Name):
            return self.lookup(node.id)
        if isinstance(node, ast.Attribute):
            path = self._name_path(node)
            return self.lookup(path)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            value = self._eval_ast(node.operand)
            return -value if isinstance(node.op, ast.USub) else value
        if isinstance(node, ast.BinOp) and isinstance(
            node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)
        ):
            left = self._eval_ast(node.left)
            right = self._eval_ast(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            return left / right
        raise SchemaError("expressions support +, -, *, /, and dimension references")

    def _name_path(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            base = self._name_path(node.value)
            return f"{base}.{node.attr}"
        raise SchemaError("unsupported expression construct")

    def resolved_tree(self) -> Dict[str, Any]:
        def build(mapping: Mapping[str, Any], prefix: str = "") -> Dict[str, Any]:
            result: Dict[str, Any] = {}
            for key, value in mapping.items():
                path = f"{prefix}.{key}" if prefix else key
                if isinstance(value, Mapping):
                    result[key] = build(value, path)
                else:
                    result[key] = self.resolve_path(path)
            return result

        return build(self.raw)


# --------------------------------------------------------------------------- #
# Basic canonicalisation helpers


def _canonical_axis(token: Any) -> AxisToken:
    if not isinstance(token, str):
        raise SchemaError(f"axis token must be a string, got {token!r}")
    text = token.strip().lower()
    if not text:
        raise SchemaError("axis token cannot be empty")
    sign = "+"
    axis = text
    if text[0] in {"+", "-"}:
        sign = text[0]
        axis = text[1:]
    elif text.endswith(("+", "-")):
        sign = text[-1]
        axis = text[:-1]
    if axis not in {"x", "y", "z"}:
        raise SchemaError(f"axis token must target x, y, or z; got '{token}'")
    return f"{sign}{axis}"


def _normalise_pos_token(token: str) -> Tuple[str, str]:
    text = token.strip().lower()
    if not text:
        raise SchemaError("position token cannot be empty")
    text = text.replace("centre_", "c").replace("center_", "c")
    text = text.replace("centre", "c").replace("center", "c")
    text = text.replace("~", "c")
    sign = "+"
    if text[0] in {"+", "-"}:
        sign = text[0]
        text = text[1:]
    pos_type = "center" if text and text[0] in CENTER_PREFIXES else "face"
    if pos_type == "center":
        text = text[1:]
    if not text or text not in {"x", "y", "z"}:
        raise SchemaError("position token must reference x, y, or z")
    return sign, text if pos_type == "face" else f"c{text}"


def canonical_pos_token(raw: Any) -> PosToken:
    tokens: List[Tuple[str, int]] = []
    if isinstance(raw, str):
        cleaned = raw.replace(" ", "")
        matches = re.findall(r"[+\-~]?c?[xyz]|c[xyz]", cleaned, flags=re.IGNORECASE)
        if not matches:
            raise SchemaError(f"position token '{raw}' must include at least one axis")
        for match in matches:
            sign, axis = _normalise_pos_token(match)
            tokens.append((axis, 0 if axis.startswith("c") else (1 if sign == "+" else -1)))
    elif isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
        for item in raw:
            sign, axis = _normalise_pos_token(str(item))
            tokens.append((axis, 0 if axis.startswith("c") else (1 if sign == "+" else -1)))
    else:
        raise SchemaError("position token must be a string or list of axes")

    seen: set[Tuple[str, int]] = set()
    unique: List[Tuple[str, int]] = []
    for axis, sign in tokens:
        key = (axis[-1], sign)
        if key in seen:
            continue
        seen.add(key)
        unique.append((axis, sign))

    def _sort_key(item: Tuple[str, int]) -> Tuple[int, int]:
        axis, sign = item
        order = { -1: 0, 0: 1, 1: 2 }.get(sign, 1)
        return (AXIS_ORDER[axis[-1]], order)

    unique.sort(key=_sort_key)
    canonical: List[str] = []
    for axis, sign in unique:
        if sign == 0 or axis.startswith("c"):
            canonical.append(f"c{axis[-1]}")
        else:
            canonical.append(f"{'+' if sign > 0 else '-'}{axis[-1]}")
    return "".join(canonical)


def _parse_frame(raw: Any) -> FrameToken:
    if raw is None:
        return "world"
    if not isinstance(raw, str):
        raise SchemaError("frame must be a string")
    value = raw.strip().lower()
    if value in VALID_FRAMES:
        return value
    if value.startswith("component:") and len(value.split(":", 1)[1]) > 0:
        return value
    raise SchemaError(f"unsupported frame '{raw}'")


def _resolve_number(value: Any, dimensions: DimensionResolver) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        return dimensions.evaluate(value)
    raise SchemaError(f"expected numeric value or expression, got {value!r}")


def _resolve_optional_number(value: Any, dimensions: DimensionResolver) -> Optional[float]:
    if value is None:
        return None
    return _resolve_number(value, dimensions)


def _resolve_metadata(value: Any, dimensions: DimensionResolver) -> Dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise SchemaError("component metadata must be a mapping when provided")
    resolved: Dict[str, Any] = {}
    for key, raw in value.items():
        if isinstance(raw, (int, float)):
            resolved[str(key)] = float(raw)
            continue
        if isinstance(raw, str):
            try:
                resolved[str(key)] = dimensions.evaluate(raw)
                continue
            except SchemaError:
                resolved[str(key)] = raw
                continue
        if isinstance(raw, Mapping):
            resolved[str(key)] = _resolve_metadata(raw, dimensions)
            continue
        resolved[str(key)] = raw
    return resolved


def _resolve_profile_params(value: Any, dimensions: DimensionResolver) -> Dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise SchemaError("profile_params must be a mapping when provided")

    def resolve(item: Any) -> Any:
        if isinstance(item, (int, float)):
            return float(item)
        if isinstance(item, str):
            try:
                return dimensions.evaluate(item)
            except SchemaError:
                return item
        if isinstance(item, Mapping):
            return {str(k): resolve(v) for k, v in item.items()}
        if isinstance(item, Sequence) and not isinstance(item, (str, bytes)):
            return [resolve(elem) for elem in item]
        return item

    return {str(key): resolve(raw) for key, raw in value.items()}


def _parse_axis_amount(value: Any, dimensions: DimensionResolver) -> Dict[PosToken, float]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return {canonical_pos_token(k): _resolve_number(v, dimensions) for k, v in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        raise SchemaError("gap/offset must be a scalar or mapping, not a list")
    return {"*": _resolve_number(value, dimensions)}


# --------------------------------------------------------------------------- #
# Data classes


@dataclass(slots=True)
class InfoBlock:
    option: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None


@dataclass(slots=True)
class DatumPoint:
    name: str
    coordinates: Dict[AxisToken, float]


@dataclass(slots=True)
class DatumPlane:
    name: str
    base: str
    normal: AxisToken
    offset: float


@dataclass(slots=True)
class DatumBundle:
    name: str
    origin: str
    span: Dict[AxisToken, float]
    translate: Dict[AxisToken, float] = field(default_factory=dict)


@dataclass(slots=True)
class AxisMapTarget:
    ref: str
    pos: PosToken
    gap: Dict[PosToken, float] = field(default_factory=dict)
    offset: Dict[PosToken, float] = field(default_factory=dict)
    mode: str = "point"
    frame: FrameToken = "world"


@dataclass(slots=True)
class AxisRelation:
    subject: PosToken
    target: AxisMapTarget


@dataclass(slots=True)
class RunBetweenSpec:
    start_relations: Tuple[AxisRelation, ...]
    end_relations: Tuple[AxisRelation, ...] = ()
    orient: str = "preserve_axes"
    count: Optional[int] = None
    pitch: Optional[float] = None
    inset_start: Optional[float] = None
    inset_end: Optional[float] = None
    include_seed: bool = False
    source: str = "run_between"


@dataclass(slots=True)
class IfcPset:
    name: str
    props: Dict[str, Any]


@dataclass(slots=True)
class IfcMetadata:
    predefined_type: Optional[str] = None
    psets: Tuple[IfcPset, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        if self.predefined_type is not None:
            data["predefined_type"] = self.predefined_type
        if self.psets:
            data["psets"] = [{"name": pset.name, "props": pset.props} for pset in self.psets]
        return data


@dataclass(slots=True)
class Placement:
    id: str
    relations: Tuple[AxisRelation, ...]


@dataclass(slots=True)
class RelationshipComponent:
    id: str
    kind: str
    class_name: Optional[str]
    profile: str
    size: Tuple[Optional[float], Optional[float], Optional[float]]
    profile_params: Dict[str, Any] = field(default_factory=dict)
    material: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    relations: Tuple[AxisRelation, ...] = ()
    run_between: Optional[RunBetweenSpec] = None
    place: Tuple[Placement, ...] = ()
    ifc: Optional[IfcMetadata] = None
    voids: Tuple[str, ...] = ()
    description: Optional[str] = None


@dataclass(slots=True)
class Operation:
    type: str


@dataclass(slots=True)
class RotateOperation(Operation):
    targets: Tuple[str, ...]
    about: str
    axis: str
    count: int = 1
    include_seed: bool = False
    id_map: Dict[str, Tuple[str, ...]] = field(default_factory=dict)


@dataclass(slots=True)
class MirrorOperation(Operation):
    targets: Tuple[str, ...]
    axis: str
    coordinate: float = 0.0
    include_seed: bool = False


@dataclass(slots=True)
class TranslateOperation(Operation):
    targets: Tuple[str, ...]
    vector: Tuple[float, float, float]
    include_seed: bool = False


@dataclass(slots=True)
class BooleanOperation(Operation):
    target: str
    subtract: Tuple[str, ...]


@dataclass(slots=True)
class AssemblyCall:
    template: str
    args: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ViewPlane:
    axis: str
    coordinate: float


@dataclass(slots=True)
class ViewConfig:
    name: str
    title: Optional[str] = None
    scale_hint: Optional[float] = None
    renders: Tuple[str, ...] = ()
    plane: Optional[ViewPlane] = None
    aria_label: Optional[str] = None
    pad: float = 48.0
    background: Optional[str] = None
    scale: Optional[float] = None


@dataclass(slots=True)
class RelationshipDiagramSpec:
    schema: str
    info: InfoBlock
    dimensions: DimensionResolver
    datums: Dict[str, DatumPoint]
    planes: Dict[str, DatumPlane]
    bundles: Dict[str, DatumBundle]
    components: Tuple[RelationshipComponent, ...]
    assemblies: Tuple[AssemblyCall, ...]
    views: Dict[str, ViewConfig]
    checks: Tuple[AxisRelation, ...] = ()
    operations: Tuple[Operation, ...] = ()


# --------------------------------------------------------------------------- #
# Parsing helpers


def load_relationship_spec(path: Path | str, *, require_schema_flag: bool = True) -> RelationshipDiagramSpec:
    path = Path(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, MutableMapping):
        raise SchemaError("relationship-first spec must be a mapping at the root")
    schema_field = raw.get("schema")
    if require_schema_flag and not is_relationship_schema(schema_field):
        raise SchemaError("schema must be marked as a relationship-first document")
    return _parse_spec(raw, source=path)


def _parse_spec(data: MutableMapping[str, Any], *, source: Path) -> RelationshipDiagramSpec:
    schema_field = str(data.get("schema") or "unknown")
    info = _parse_info(data.get("info", {}))
    dimensions = DimensionResolver.from_mapping(data.get("dimensions"))
    datums, planes, bundles = _parse_datums(data.get("datums", {}), dimensions)
    checks = tuple(_parse_axis_map(data.get("checks", {}), dimensions))
    components, assemblies = _parse_components(data.get("components", []), dimensions)
    views = _parse_views(data.get("views", {}), dimensions)
    operations = tuple(_parse_operations(data.get("operations", ()), dimensions))
    return RelationshipDiagramSpec(
        schema=schema_field,
        info=info,
        dimensions=dimensions,
        datums=datums,
        planes=planes,
        bundles=bundles,
        components=components,
        assemblies=assemblies,
        views=views,
        checks=checks,
        operations=operations,
    )


def _parse_info(data: Mapping[str, Any]) -> InfoBlock:
    if not isinstance(data, Mapping):
        raise SchemaError("info block must be a mapping when provided")
    return InfoBlock(
        option=str(data.get("option")) if data.get("option") is not None else None,
        title=str(data.get("title")) if data.get("title") is not None else None,
        description=str(data.get("description")) if data.get("description") is not None else None,
    )


def _parse_datums(
    data: Mapping[str, Any],
    dimensions: DimensionResolver,
) -> Tuple[Dict[str, DatumPoint], Dict[str, DatumPlane], Dict[str, DatumBundle]]:
    if not isinstance(data, Mapping):
        raise SchemaError("datums must be a mapping")

    points: Dict[str, DatumPoint] = {}
    planes: Dict[str, DatumPlane] = {}
    bundles: Dict[str, DatumBundle] = {}

    for key, value in data.items():
        if key == "planes":
            planes.update(_parse_plane_block(value, dimensions))
            continue
        if key == "bundles":
            bundles.update(_parse_bundle_block(value, dimensions))
            continue
        point = _parse_point(key, value, dimensions)
        points[point.name] = point

    return points, planes, bundles


def _parse_point(name: str, value: Any, dimensions: DimensionResolver) -> DatumPoint:
    if not isinstance(value, Mapping):
        raise SchemaError("datum point must be a mapping")
    dtype = value.get("type", "point")
    if dtype != "point":
        raise SchemaError(f"datum '{name}' must have type 'point'")
    coords_raw = value.get("coordinates")
    if not isinstance(coords_raw, Mapping):
        raise SchemaError(f"datum '{name}' coordinates must be a mapping of axes")
    coords: Dict[AxisToken, float] = {}
    for axis, raw in coords_raw.items():
        axis_token = _canonical_axis(axis)
        coords[axis_token] = _resolve_number(raw, dimensions)
    if not coords:
        raise SchemaError(f"datum '{name}' requires at least one coordinate")
    return DatumPoint(name=name, coordinates=coords)


def _parse_plane_block(data: Any, dimensions: DimensionResolver) -> Dict[str, DatumPlane]:
    if not isinstance(data, Mapping):
        raise SchemaError("datums.planes must be a mapping")
    planes: Dict[str, DatumPlane] = {}
    for name, value in data.items():
        if not isinstance(value, Mapping):
            raise SchemaError(f"datum plane '{name}' must be a mapping")
        base_raw = value.get("base")
        if not isinstance(base_raw, Mapping) or "ref" not in base_raw:
            raise SchemaError(f"datum plane '{name}' requires base.ref")
        normal_raw = value.get("normal")
        if normal_raw is None:
            raise SchemaError(f"datum plane '{name}' requires a normal axis")
        offset_raw = value.get("offset", 0.0)
        planes[name] = DatumPlane(
            name=name,
            base=str(base_raw["ref"]),
            normal=_canonical_axis(normal_raw),
            offset=_resolve_number(offset_raw, dimensions),
        )
    return planes


def _parse_bundle_block(data: Any, dimensions: DimensionResolver) -> Dict[str, DatumBundle]:
    if not isinstance(data, Mapping):
        raise SchemaError("datums.bundles must be a mapping")
    bundles: Dict[str, DatumBundle] = {}
    for name, value in data.items():
        if not isinstance(value, Mapping):
            raise SchemaError(f"datum bundle '{name}' must be a mapping")
        origin_raw = value.get("origin")
        if not isinstance(origin_raw, Mapping) or "ref" not in origin_raw:
            raise SchemaError(f"datum bundle '{name}' requires origin.ref")
        span_raw = value.get("span")
        if not isinstance(span_raw, Mapping):
            raise SchemaError(f"datum bundle '{name}' requires a span mapping")
        span: Dict[AxisToken, float] = {}
        for axis, raw in span_raw.items():
            axis_token = _canonical_axis(axis)
            span[axis_token] = _resolve_number(raw, dimensions)
        translate_raw = value.get("translate", {})
        translate: Dict[AxisToken, float] = {}
        if translate_raw:
            if not isinstance(translate_raw, Mapping):
                raise SchemaError(f"datum bundle '{name}' translate must be a mapping")
            for axis, raw in translate_raw.items():
                axis_token = _canonical_axis(axis)
                translate[axis_token] = _resolve_number(raw, dimensions)
        bundles[name] = DatumBundle(
            name=name,
            origin=str(origin_raw["ref"]),
            span=span,
            translate=translate,
        )
    return bundles


def _parse_size(raw: Any, dimensions: DimensionResolver) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    if raw is None:
        return (None, None, None)
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        raise SchemaError("size must be a list when provided")
    values = []
    for item in raw:
        if item is None:
            values.append(None)
        else:
            values.append(_resolve_number(item, dimensions))
    if len(values) == 2:
        return (values[0], values[1], None)
    if len(values) == 3:
        return (values[0], values[1], values[2])
    raise SchemaError("size must have 2 or 3 entries")


def _parse_components(
    data: Sequence[Any],
    dimensions: DimensionResolver,
) -> Tuple[Tuple[RelationshipComponent, ...], Tuple[AssemblyCall, ...]]:
    if not isinstance(data, Sequence):
        raise SchemaError("components must be a list")
    components: List[RelationshipComponent] = []
    assemblies: List[AssemblyCall] = []
    for entry in data:
        if not isinstance(entry, Mapping):
            raise SchemaError("component entries must be mappings")
        if "use" in entry:
            assemblies.append(_parse_assembly(entry))
            continue
        components.append(_parse_component(entry, dimensions))
    _ensure_unique_ids(components)
    return tuple(components), tuple(assemblies)


def _parse_component(data: Mapping[str, Any], dimensions: DimensionResolver) -> RelationshipComponent:
    if "id" not in data:
        raise SchemaError("component requires an id")
    comp_id = str(data["id"])
    kind = str(data.get("kind", "component")).lower()
    class_raw = data.get("class")
    class_name = normalize_ifc_class(class_raw) if class_raw else None
    profile = str(data.get("profile", "rectangle"))
    profile_params = _resolve_profile_params(data.get("profile_params"), dimensions)
    size = _parse_size(data.get("size"), dimensions)

    metadata = _resolve_metadata(data.get("metadata"), dimensions)
    label = data.get("label")
    if label is not None:
        metadata.setdefault("label", str(label))
    label_id = data.get("label_id")
    if label_id is not None:
        metadata.setdefault("label_id", str(label_id))
    views_raw = data.get("views")
    if views_raw is not None:
        if not isinstance(views_raw, Sequence) or isinstance(views_raw, (str, bytes)):
            raise SchemaError(f"component '{comp_id}' views must be a list when provided")
        metadata.setdefault("views", tuple(str(view) for view in views_raw))

    ifc_block = _parse_ifc_block(data.get("ifc"))
    voids_raw = data.get("voids", ())
    voids: List[str] = []
    if voids_raw:
        if not isinstance(voids_raw, Sequence) or isinstance(voids_raw, (str, bytes)):
            raise SchemaError(f"component '{comp_id}' voids must be a list when provided")
        for entry in voids_raw:
            if isinstance(entry, Mapping):
                ref = entry.get("ref")
                if ref is None:
                    raise SchemaError(f"component '{comp_id}' void entry requires 'ref'")
                voids.append(str(ref))
            else:
                voids.append(str(entry))
    relations = tuple(_parse_axis_map(data.get("relate", {}), dimensions))
    array_raw = data.get("array")
    run_between_raw = data.get("run_between")
    if array_raw is not None and run_between_raw is not None:
        raise SchemaError(f"component '{comp_id}' cannot specify both array and run_between")
    run_between = _parse_run_between(array_raw, dimensions, source="array") if array_raw is not None else _parse_run_between(run_between_raw, dimensions)
    place = tuple(_parse_place(data.get("place", ()), dimensions))
    description = str(data["description"]) if "description" in data else None
    material = str(data["material"]) if data.get("material") is not None else None

    return RelationshipComponent(
        id=comp_id,
        kind=kind,
        class_name=class_name,
        profile=profile,
        profile_params=profile_params,
        size=size,
        material=material,
        metadata=metadata,
        relations=relations,
        run_between=run_between,
        place=place,
        ifc=ifc_block,
        voids=tuple(voids),
        description=description,
    )


def _parse_ifc_block(data: Any) -> Optional[IfcMetadata]:
    if data is None:
        return None
    if not isinstance(data, Mapping):
        raise SchemaError("ifc block must be a mapping")
    predefined = data.get("predefined_type")
    psets_raw = data.get("psets", ())
    psets: List[IfcPset] = []
    if psets_raw:
        if not isinstance(psets_raw, Sequence):
            raise SchemaError("ifc.psets must be a list when provided")
        for item in psets_raw:
            if not isinstance(item, Mapping):
                raise SchemaError("ifc.psets entries must be mappings")
            if "name" not in item or "props" not in item:
                raise SchemaError("ifc.psets entries require 'name' and 'props'")
            props_raw = item.get("props")
            if not isinstance(props_raw, Mapping):
                raise SchemaError("ifc.psets.props must be a mapping")
            psets.append(IfcPset(name=normalize_pset_name(item["name"]), props=dict(props_raw)))
    predefined_norm = normalize_ifc_predefined_type(predefined)
    return IfcMetadata(predefined_type=predefined_norm, psets=tuple(psets))


def _parse_axis_map(data: Any, dimensions: DimensionResolver) -> List[AxisRelation]:
    if data is None:
        return []
    items: List[Tuple[Any, Any]] = []
    if isinstance(data, Mapping):
        items = list(data.items())
    elif isinstance(data, Sequence):
        for entry in data:
            if not isinstance(entry, Mapping) or len(entry) != 1:
                raise SchemaError("axis-map entries must be single-key mappings")
            key = next(iter(entry.keys()))
            items.append((key, entry[key]))
    else:
        raise SchemaError("axis-map must be a mapping or list when provided")

    relations: List[AxisRelation] = []
    for raw_subject, payload in items:
        if raw_subject == "flush":
            relations.extend(_parse_flush(payload, dimensions))
            continue
        subject = canonical_pos_token(raw_subject)
        if not isinstance(payload, Mapping):
            raise SchemaError("axis-map entry must be a mapping")
        ref_raw = payload.get("ref") or payload.get("component") or payload.get("to")
        if ref_raw is None:
            raise SchemaError(f"axis-map entry '{subject}' requires a ref/component/to field")
        pos_raw = payload.get("pos", subject)
        gap = _parse_axis_amount(payload.get("gap"), dimensions)
        offset = _parse_axis_amount(payload.get("offset"), dimensions)
        mode = str(payload.get("mode", "point"))
        frame = _parse_frame(payload.get("frame"))
        relations.append(
            AxisRelation(
                subject=subject,
                target=AxisMapTarget(
                    ref=str(ref_raw),
                    pos=canonical_pos_token(pos_raw),
                    gap=gap,
                    offset=offset,
                    mode=mode,
                    frame=frame,
                ),
            )
        )
    return relations


def _parse_flush(payload: Any, dimensions: DimensionResolver) -> List[AxisRelation]:
    if not isinstance(payload, Mapping):
        raise SchemaError("flush must be a mapping")
    ref_raw = payload.get("ref") or payload.get("component") or payload.get("to")
    if ref_raw is None:
        raise SchemaError("flush requires a ref/component/to field")
    frame = _parse_frame(payload.get("frame"))
    faces_raw = payload.get("faces") or ("+x", "-x", "+y", "-y", "+z", "-z")
    if isinstance(faces_raw, str):
        faces = [faces_raw]
    elif isinstance(faces_raw, Sequence):
        faces = list(faces_raw)
    else:
        raise SchemaError("flush.faces must be a list or string")

    inset_raw = payload.get("inset", 0.0)
    inset_map: Dict[PosToken, float] = {}
    if isinstance(inset_raw, Mapping):
        inset_map = {canonical_pos_token(k): _resolve_number(v, dimensions) for k, v in inset_raw.items()}
    else:
        inset_value = _resolve_number(inset_raw, dimensions)
        inset_map = {"*": inset_value}

    relations: List[AxisRelation] = []
    for face in faces:
        subject = canonical_pos_token(face)
        gap = inset_map.copy()
        relations.append(
            AxisRelation(
                subject=subject,
                target=AxisMapTarget(
                    ref=str(ref_raw),
                    pos=subject,
                    gap=gap,
                    mode="plane",
                    frame=frame,
                ),
            )
        )
    return relations


def _parse_run_between(payload: Any, dimensions: DimensionResolver, *, source: str = "run_between") -> Optional[RunBetweenSpec]:
    if payload is None:
        return None
    if not isinstance(payload, Mapping):
        raise SchemaError(f"{source} must be a mapping")
    start_raw = payload.get("start")
    end_raw = payload.get("end")
    if start_raw is None:
        raise SchemaError(f"{source} requires a start axis-map")
    if not isinstance(start_raw, Mapping):
        raise SchemaError(f"{source}.start must be a mapping")
    if end_raw is not None and not isinstance(end_raw, Mapping):
        raise SchemaError(f"{source}.end must be a mapping when provided")
    orient = str(payload.get("orient", "preserve_axes"))
    count = payload.get("count")
    pitch = payload.get("pitch")
    if (count is not None or pitch is not None) and end_raw is None:
        raise SchemaError(f"{source} with count/pitch requires an end axis-map")
    inset = payload.get("inset", {}) or {}
    inset_start = _resolve_optional_number(inset.get("start"), dimensions) if isinstance(inset, Mapping) else None
    inset_end = _resolve_optional_number(inset.get("end"), dimensions) if isinstance(inset, Mapping) else None
    include_seed = bool(payload.get("include_seed", False))
    return RunBetweenSpec(
        start_relations=tuple(_parse_axis_map(start_raw, dimensions)),
        end_relations=tuple(_parse_axis_map(end_raw, dimensions)) if end_raw is not None else tuple(),
        orient=orient,
        count=int(count) if count is not None else None,
        pitch=_resolve_optional_number(pitch, dimensions),
        inset_start=inset_start,
        inset_end=inset_end,
        include_seed=include_seed,
        source=source,
    )


def _parse_axis_target(data: Mapping[str, Any], dimensions: DimensionResolver) -> AxisMapTarget:
    if not isinstance(data, Mapping):
        raise SchemaError("axis target must be a mapping")
    ref_raw = data.get("ref") or data.get("component") or data.get("bundle") or data.get("datum") or data.get("object")
    if ref_raw is None:
        raise SchemaError("axis target requires a reference")
    pos_raw = data.get("pos") or data.get("face")
    if pos_raw is None:
        raise SchemaError("axis target requires 'pos'")
    frame = _parse_frame(data.get("frame"))
    return AxisMapTarget(
        ref=str(ref_raw),
        pos=canonical_pos_token(pos_raw),
        gap=_parse_axis_amount(data.get("gap"), dimensions),
        offset=_parse_axis_amount(data.get("offset"), dimensions),
        mode=str(data.get("mode", "point")),
        frame=frame,
    )


def _parse_place(data: Any, dimensions: DimensionResolver) -> List[Placement]:
    if data is None:
        return []
    if not isinstance(data, Sequence):
        raise SchemaError("place must be a list when provided")
    placements: List[Placement] = []
    for entry in data:
        if not isinstance(entry, Mapping):
            raise SchemaError("place entries must be mappings")
        place_id = entry.get("id")
        if not place_id:
            raise SchemaError("place entries require an id")
        axis_map_payload = {k: v for k, v in entry.items() if k != "id"}
        relations = tuple(_parse_axis_map(axis_map_payload, dimensions))
        placements.append(Placement(id=str(place_id), relations=relations))
    return placements


def _parse_assembly(data: Mapping[str, Any]) -> AssemblyCall:
    template = data.get("use")
    if template is None:
        raise SchemaError("assembly entries require 'use'")
    args_raw = data.get("with", {}) or {}
    if not isinstance(args_raw, Mapping):
        raise SchemaError("assembly 'with' block must be a mapping")
    return AssemblyCall(template=str(template), args=dict(args_raw))


def _ensure_unique_ids(components: Sequence[RelationshipComponent]) -> None:
    seen: set[str] = set()
    for component in components:
        if component.id in seen:
            raise SchemaError(f"duplicate component id '{component.id}'")
        seen.add(component.id)


def _parse_operations(data: Any, dimensions: DimensionResolver) -> List[Operation]:
    if data is None:
        return []
    if not isinstance(data, Sequence):
        raise SchemaError("operations must be a list when provided")
    operations: List[Operation] = []
    for entry in data:
        if not isinstance(entry, Mapping):
            raise SchemaError("operation entries must be mappings")
        op_type = str(entry.get("type", "")).lower()
        if op_type == "rotate":
            operations.append(_parse_rotate_operation(entry, dimensions))
        elif op_type == "mirror":
            operations.append(_parse_mirror_operation(entry, dimensions))
        elif op_type == "translate":
            operations.append(_parse_translate_operation(entry, dimensions))
        elif op_type == "boolean":
            operations.append(_parse_boolean_operation(entry))
        else:
            raise SchemaError(f"unsupported operation type '{op_type}'")
    return operations


def _parse_targets(entry: Mapping[str, Any]) -> Tuple[str, ...]:
    targets_raw = entry.get("targets") or entry.get("components") or entry.get("ids")
    if targets_raw is None:
        return ()
    if not isinstance(targets_raw, Sequence) or isinstance(targets_raw, (str, bytes)):
        raise SchemaError("operation targets must be a list when provided")
    return tuple(str(t) for t in targets_raw)


def _parse_rotate_operation(entry: Mapping[str, Any], dimensions: DimensionResolver) -> RotateOperation:
    about_raw = entry.get("about") or {}
    if not isinstance(about_raw, Mapping) or "ref" not in about_raw:
        raise SchemaError("rotate operation requires about.ref")
    axis_raw = about_raw.get("axis", "+z")
    axis_token = _canonical_axis(axis_raw)
    count_raw = entry.get("count", 1)
    count = int(count_raw) if count_raw is not None else 1
    include_seed = bool(entry.get("include_seed", False))
    id_map_raw = entry.get("id_map", {}) or {}
    if not isinstance(id_map_raw, Mapping):
        raise SchemaError("rotate.id_map must be a mapping when provided")
    id_map: Dict[str, Tuple[str, ...]] = {}
    for base, mapped in id_map_raw.items():
        if not isinstance(mapped, Sequence) or isinstance(mapped, (str, bytes)):
            raise SchemaError("rotate.id_map values must be lists")
        id_map[str(base)] = tuple(str(item) for item in mapped)
    targets = _parse_targets(entry)
    if not targets and id_map:
        targets = tuple(id_map.keys())
    return RotateOperation(
        type="rotate",
        targets=targets,
        about=str(about_raw["ref"]),
        axis=axis_token,
        count=count,
        include_seed=include_seed,
        id_map=id_map,
    )


def _parse_mirror_operation(entry: Mapping[str, Any], dimensions: DimensionResolver) -> MirrorOperation:
    plane_raw = entry.get("plane") or {}
    if not isinstance(plane_raw, Mapping):
        raise SchemaError("mirror.plane must be a mapping")
    axis_raw = plane_raw.get("axis", "x")
    axis_token = _canonical_axis(axis_raw)[-1]
    coordinate = _resolve_number(plane_raw.get("coordinate", 0.0), dimensions)
    targets = _parse_targets(entry)
    include_seed = bool(entry.get("include_seed", False))
    return MirrorOperation(type="mirror", targets=targets, axis=axis_token, coordinate=coordinate, include_seed=include_seed)


def _parse_translate_operation(entry: Mapping[str, Any], dimensions: DimensionResolver) -> TranslateOperation:
    vector_raw = entry.get("vector") or entry.get("offset") or {}
    if not isinstance(vector_raw, Mapping):
        raise SchemaError("translate.vector must be a mapping")
    vector = (
        _resolve_number(vector_raw.get("x", 0.0), dimensions),
        _resolve_number(vector_raw.get("y", 0.0), dimensions),
        _resolve_number(vector_raw.get("z", 0.0), dimensions),
    )
    targets = _parse_targets(entry)
    include_seed = bool(entry.get("include_seed", False))
    return TranslateOperation(type="translate", targets=targets, vector=vector, include_seed=include_seed)


def _parse_boolean_operation(entry: Mapping[str, Any]) -> BooleanOperation:
    target = entry.get("target")
    subtract_raw = entry.get("subtract") or ()
    if target is None:
        raise SchemaError("boolean operation requires a target")
    if not isinstance(subtract_raw, Sequence) or isinstance(subtract_raw, (str, bytes)):
        raise SchemaError("boolean.subtract must be a list")
    subtract = tuple(str(item) for item in subtract_raw)
    return BooleanOperation(type="boolean", target=str(target), subtract=subtract)


def _parse_views(data: Any, dimensions: DimensionResolver) -> Dict[str, ViewConfig]:
    if data is None:
        return {}
    if not isinstance(data, Mapping):
        raise SchemaError("views block must be a mapping when provided")
    views: Dict[str, ViewConfig] = {}
    for name, raw in data.items():
        if not isinstance(raw, Mapping):
            raise SchemaError("view entries must be mappings")
        plane_raw = raw.get("plane")
        plane = None
        if plane_raw is not None:
            if not isinstance(plane_raw, Mapping):
                raise SchemaError("view.plane must be a mapping")
            axis = plane_raw.get("axis")
            coordinate = plane_raw.get("coordinate")
            if axis not in {"x", "y"}:
                raise SchemaError("view.plane.axis must be 'x' or 'y'")
            if coordinate is None:
                raise SchemaError("view.plane requires a coordinate")
            plane = ViewPlane(axis=str(axis), coordinate=_resolve_number(coordinate, dimensions))
        renders_raw = raw.get("renders", ())
        renders: Tuple[str, ...] = ()
        if renders_raw:
            if not isinstance(renders_raw, Sequence):
                raise SchemaError("view.renders must be a list")
            renders = tuple(str(item) for item in renders_raw)
        scale_hint_raw = raw.get("scale_hint", raw.get("scale"))
        scale_hint = _resolve_optional_number(scale_hint_raw, dimensions) if scale_hint_raw is not None else None
        pad_value = _resolve_number(raw.get("pad", 48.0), dimensions)
        background = str(raw.get("background")) if raw.get("background") is not None else None
        views[name] = ViewConfig(
            name=str(name),
            title=str(raw.get("title")) if raw.get("title") is not None else None,
            scale_hint=scale_hint,
            renders=renders,
            plane=plane,
            aria_label=str(raw.get("aria_label")) if raw.get("aria_label") is not None else None,
            pad=pad_value,
            background=background,
            scale=scale_hint,
        )
    return views


__all__ = [
    "AxisMapTarget",
    "AxisRelation",
    "BooleanOperation",
    "DatumBundle",
    "DatumPlane",
    "DatumPoint",
    "DimensionResolver",
    "IfcMetadata",
    "InfoBlock",
    "MirrorOperation",
    "Placement",
    "PosToken",
    "RelationshipComponent",
    "RelationshipDiagramSpec",
    "RotateOperation",
    "RunBetweenSpec",
    "SchemaError",
    "TranslateOperation",
    "canonical_pos_token",
    "load_relationship_spec",
]
