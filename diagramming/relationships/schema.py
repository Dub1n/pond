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


def canonical_pos_token(raw: Any) -> PosToken:
    tokens: List[Tuple[str, str]] = []
    if isinstance(raw, str):
        text = raw.replace(" ", "")
        matches = re.findall(r"[+-][xyz]", text)
        if not matches:
            raise SchemaError(f"position token '{raw}' must include at least one signed axis")
        for item in matches:
            tokens.append((item[1], item[0]))
    elif isinstance(raw, Sequence):
        for item in raw:
            axis_token = _canonical_axis(item)
            tokens.append((axis_token[1], axis_token[0]))
    else:
        raise SchemaError("position token must be a string or list of axes")

    seen: set[str] = set()
    unique: List[Tuple[str, str]] = []
    for axis, sign in tokens:
        if axis in seen:
            raise SchemaError(f"position token '{raw}' repeats axis '{axis}'")
        seen.add(axis)
        unique.append((axis, sign))

    unique.sort(key=lambda item: AXIS_ORDER[item[0]])
    return "".join(f"{sign}{axis}" for axis, sign in unique)


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
class AlignmentTarget:
    ref: str
    pos: PosToken
    frame: FrameToken = "world"


@dataclass(slots=True)
class AlignmentClause:
    kind: str
    subject: AlignmentTarget
    obj: AlignmentTarget
    gap: float = 0.0
    tolerance: float = 0.5
    on_fail: str = "error"


@dataclass(slots=True)
class FlushFace:
    subject: PosToken
    obj: PosToken


@dataclass(slots=True)
class FlushBundleClause:
    bundle: str
    faces: Tuple[FlushFace, ...]
    inset_subject: Dict[PosToken, float] = field(default_factory=dict)
    inset_object: Dict[PosToken, float] = field(default_factory=dict)
    frame: FrameToken = "world"


@dataclass(slots=True)
class RunBetweenClause:
    start_pos: PosToken
    end_pos: PosToken
    from_ref: AlignmentTarget
    to_ref: AlignmentTarget
    orient: str = "preserve_axes"
    count: Optional[int] = None
    pitch: Optional[float] = None
    inset_start: Optional[float] = None
    inset_end: Optional[float] = None
    include_seed: bool = False


@dataclass(slots=True)
class RelateFromClause:
    source: str
    overrides: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RepeatSpec:
    axis: AxisToken
    span_use: Optional[str] = None
    pitch: Optional[float] = None
    count: Optional[int] = None
    inset_start: float = 0.0
    inset_end: float = 0.0
    include_seed: bool = False


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
class RelationshipComponent:
    id: str
    class_name: str
    profile: str
    size_xy: Tuple[float, float]
    height: float
    profile_params: Dict[str, Any] = field(default_factory=dict)
    material: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    relationships: Tuple[AlignmentClause | FlushBundleClause | RunBetweenClause | RelateFromClause, ...] = ()
    repeat: Optional[RepeatSpec] = None
    ifc: Optional[IfcMetadata] = None
    voids: Tuple[str, ...] = ()
    description: Optional[str] = None


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
    checks: Tuple[AlignmentClause, ...] = ()


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
    checks = tuple(_parse_checks(data.get("checks", ()), dimensions))
    components, assemblies = _parse_components(data.get("components", []), dimensions)
    views = _parse_views(data.get("views", {}), dimensions)
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
    if "class" not in data:
        raise SchemaError(f"component '{data['id']}' requires a class")
    if "size" not in data:
        raise SchemaError(f"component '{data['id']}' requires size")
    comp_id = str(data["id"])
    class_name = normalize_ifc_class(data["class"])
    profile = str(data.get("profile", "rectangle"))
    profile_params = _resolve_profile_params(data.get("profile_params"), dimensions)

    size_raw = data["size"]
    if not isinstance(size_raw, Sequence):
        raise SchemaError(f"component '{comp_id}' size must be a sequence")
    resolved_size = [_resolve_number(item, dimensions) for item in size_raw]
    if len(resolved_size) not in (2, 3):
        raise SchemaError(f"component '{comp_id}' size must have 2 or 3 entries")
    size_xy = (resolved_size[0], resolved_size[1])
    height = resolved_size[2] if len(resolved_size) == 3 else _resolve_number(data.get("height", 0.0), dimensions)

    metadata = _resolve_metadata(data.get("metadata"), dimensions)
    ifc_block = _parse_ifc_block(data.get("ifc"))
    voids = tuple(str(item) for item in data.get("voids", ()))
    repeat = _parse_repeat(data.get("repeat"), dimensions)
    relationships = tuple(_parse_relationships(data.get("relate", ()), dimensions))
    description = str(data["description"]) if "description" in data else None
    material = str(data["material"]) if data.get("material") is not None else None

    return RelationshipComponent(
        id=comp_id,
        class_name=class_name,
        profile=profile,
        profile_params=profile_params,
        size_xy=size_xy,
        height=height,
        material=material,
        metadata=metadata,
        relationships=relationships,
        repeat=repeat,
        ifc=ifc_block,
        voids=voids,
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


def _parse_relationships(data: Any, dimensions: DimensionResolver) -> List[Any]:
    if data is None:
        return []
    if not isinstance(data, Sequence):
        raise SchemaError("relate block must be a list when provided")
    clauses: List[Any] = []
    for entry in data:
        if not isinstance(entry, Mapping) or len(entry) != 1:
            raise SchemaError("each relate entry must be a single-key mapping")
        key = next(iter(entry.keys()))
        payload = entry[key]
        if key in {"align", "contact"}:
            clauses.append(_parse_align_clause(key, payload, dimensions))
        elif key == "flush_bundle":
            clauses.append(_parse_flush_bundle(payload, dimensions))
        elif key == "run_between":
            clauses.append(_parse_run_between(payload, dimensions))
        elif key == "relate_from":
            clauses.append(_parse_relate_from(payload))
        elif key == "touch_planes":
            clauses.extend(_parse_touch_planes(payload, dimensions))
        elif key == "touch_components":
            clauses.extend(_parse_touch_components(payload, dimensions))
        else:
            raise SchemaError(f"unsupported relate helper '{key}'")
    return clauses


def _parse_align_clause(kind: str, payload: Any, dimensions: DimensionResolver) -> AlignmentClause:
    if not isinstance(payload, Mapping):
        raise SchemaError(f"{kind} clause must be a mapping")
    subject_raw = payload.get("subject")
    object_raw = payload.get("object")
    if subject_raw is None or object_raw is None:
        raise SchemaError(f"{kind} clause requires 'subject' and 'object'")
    subject = _parse_alignment_target(subject_raw, dimensions)
    obj = _parse_alignment_target(object_raw, dimensions)
    gap = _resolve_number(payload.get("gap", 0.0), dimensions)
    tolerance = _resolve_number(payload.get("tolerance", 0.5), dimensions)
    on_fail = str(payload.get("on_fail", "error"))
    if kind == "contact":
        gap = 0.0
    return AlignmentClause(kind=kind, subject=subject, obj=obj, gap=gap, tolerance=tolerance, on_fail=on_fail)


def _parse_alignment_target(data: Any, dimensions: DimensionResolver) -> AlignmentTarget:
    if not isinstance(data, Mapping):
        raise SchemaError("alignment target must be a mapping")
    pos_raw = data.get("pos") or data.get("face")
    if pos_raw is None:
        raise SchemaError("alignment target requires 'pos'")
    ref = (
        data.get("component")
        or data.get("bundle")
        or data.get("datum")
        or data.get("ref")
        or data.get("object")
    )
    if ref is None:
        raise SchemaError("alignment target requires a reference (component/datum/bundle)")
    frame = _parse_frame(data.get("frame"))
    return AlignmentTarget(ref=str(ref), pos=canonical_pos_token(pos_raw), frame=frame)


def _parse_flush_bundle(payload: Any, dimensions: DimensionResolver) -> FlushBundleClause:
    if not isinstance(payload, Mapping):
        raise SchemaError("flush_bundle must be a mapping")
    bundle = payload.get("bundle")
    if bundle is None:
        raise SchemaError("flush_bundle requires 'bundle'")
    faces_raw = payload.get("faces")
    if faces_raw is None:
        raise SchemaError("flush_bundle requires 'faces'")
    faces: List[FlushFace] = []
    if not isinstance(faces_raw, Sequence):
        raise SchemaError("flush_bundle.faces must be a list")
    for face_entry in faces_raw:
        if isinstance(face_entry, Mapping):
            subject_pos = face_entry.get("subject") or face_entry.get("face")
            object_pos = face_entry.get("object") or face_entry.get("bundle") or face_entry.get("target") or subject_pos
        else:
            subject_pos = face_entry
            object_pos = face_entry
        if subject_pos is None or object_pos is None:
            raise SchemaError("flush_bundle face entries require subject/object faces")
        faces.append(
            FlushFace(subject=canonical_pos_token(subject_pos), obj=canonical_pos_token(object_pos))
        )

    inset_raw = payload.get("inset", {}) or {}
    inset_subject: Dict[PosToken, float] = {}
    inset_object: Dict[PosToken, float] = {}
    if inset_raw:
        if not isinstance(inset_raw, Mapping):
            raise SchemaError("flush_bundle.inset must be a mapping when provided")
        subject_map = inset_raw.get("subject", inset_raw)
        object_map = inset_raw.get("object", {})
        if subject_map:
            for face, raw in subject_map.items():
                inset_subject[canonical_pos_token(face)] = _resolve_number(raw, dimensions)
        if object_map:
            for face, raw in object_map.items():
                inset_object[canonical_pos_token(face)] = _resolve_number(raw, dimensions)

    frame = _parse_frame(payload.get("frame"))
    return FlushBundleClause(
        bundle=str(bundle),
        faces=tuple(faces),
        inset_subject=inset_subject,
        inset_object=inset_object,
        frame=frame,
    )


def _parse_run_between(payload: Any, dimensions: DimensionResolver) -> RunBetweenClause:
    if not isinstance(payload, Mapping):
        raise SchemaError("run_between must be a mapping")
    start_pos = payload.get("start_pos")
    if start_pos is None:
        raise SchemaError("run_between requires start_pos")
    end_pos = payload.get("end_pos", start_pos)
    from_raw = payload.get("from")
    to_raw = payload.get("to")
    if from_raw is None or to_raw is None:
        raise SchemaError("run_between requires 'from' and 'to'")
    orient = str(payload.get("orient", "preserve_axes"))
    count = payload.get("count")
    pitch = payload.get("pitch")
    inset = payload.get("inset", {}) or {}
    inset_start = _resolve_optional_number(inset.get("start"), dimensions) if isinstance(inset, Mapping) else None
    inset_end = _resolve_optional_number(inset.get("end"), dimensions) if isinstance(inset, Mapping) else None
    include_seed = bool(payload.get("include_seed", False))
    return RunBetweenClause(
        start_pos=canonical_pos_token(start_pos),
        end_pos=canonical_pos_token(end_pos),
        from_ref=_parse_alignment_target(from_raw, dimensions),
        to_ref=_parse_alignment_target(to_raw, dimensions),
        orient=orient,
        count=int(count) if count is not None else None,
        pitch=_resolve_optional_number(pitch, dimensions),
        inset_start=inset_start,
        inset_end=inset_end,
        include_seed=include_seed,
    )


def _parse_relate_from(payload: Any) -> RelateFromClause:
    if not isinstance(payload, Mapping):
        raise SchemaError("relate_from must be a mapping")
    source = payload.get("source")
    if source is None:
        raise SchemaError("relate_from requires 'source'")
    overrides_raw = payload.get("overrides", {})
    if overrides_raw and not isinstance(overrides_raw, Mapping):
        raise SchemaError("relate_from.overrides must be a mapping")
    return RelateFromClause(source=str(source), overrides=dict(overrides_raw or {}))


def _parse_touch_planes(payload: Any, dimensions: DimensionResolver) -> List[AlignmentClause]:
    if not isinstance(payload, Mapping):
        raise SchemaError("touch_planes must be a mapping")
    object_ref = payload.get("object")
    faces_raw = payload.get("faces")
    if object_ref is None or faces_raw is None:
        raise SchemaError("touch_planes requires 'object' and 'faces'")
    if not isinstance(faces_raw, Sequence):
        raise SchemaError("touch_planes.faces must be a list")
    clauses: List[AlignmentClause] = []
    for face in faces_raw:
        subject = AlignmentTarget(ref="self", pos=canonical_pos_token(face), frame="local")
        obj = AlignmentTarget(ref=str(object_ref), pos=canonical_pos_token(face), frame="world")
        clauses.append(
            AlignmentClause(kind="contact", subject=subject, obj=obj, gap=0.0, tolerance=0.5, on_fail="error")
        )
    return clauses


def _parse_touch_components(payload: Any, dimensions: DimensionResolver) -> List[AlignmentClause]:
    if not isinstance(payload, Mapping):
        raise SchemaError("touch_components must be a mapping")
    pairs_raw = payload.get("pairs")
    if not isinstance(pairs_raw, Sequence):
        raise SchemaError("touch_components requires a list of pairs")
    clauses: List[AlignmentClause] = []
    offsets_raw = payload.get("offsets", {})
    default_gap = _resolve_number(offsets_raw.get("gap", 0.0) if isinstance(offsets_raw, Mapping) else 0.0, dimensions)
    for pair in pairs_raw:
        if not isinstance(pair, Mapping):
            raise SchemaError("touch_components pairs must be mappings")
        subject_face = pair.get("subject_face")
        object_face = pair.get("object_face")
        object_component = pair.get("object_component")
        if subject_face is None or object_face is None or object_component is None:
            raise SchemaError("touch_components pairs require subject_face, object_face, object_component")
        subject = AlignmentTarget(ref="self", pos=canonical_pos_token(subject_face), frame="local")
        obj = AlignmentTarget(ref=str(object_component), pos=canonical_pos_token(object_face), frame="world")
        gap_value = pair.get("gap", default_gap)
        clauses.append(
            AlignmentClause(
                kind="contact",
                subject=subject,
                obj=obj,
                gap=_resolve_number(gap_value, dimensions),
                tolerance=0.5,
                on_fail="error",
            )
        )
    return clauses


def _parse_repeat(data: Any, dimensions: DimensionResolver) -> Optional[RepeatSpec]:
    if data is None:
        return None
    if not isinstance(data, Mapping):
        raise SchemaError("repeat must be a mapping when provided")
    axis_raw = data.get("axis")
    if axis_raw is None:
        raise SchemaError("repeat requires 'axis'")
    axis = _canonical_axis(axis_raw)
    span_raw = data.get("span") or {}
    span_use = None
    inset_start = 0.0
    inset_end = 0.0
    if isinstance(span_raw, Mapping) and "use" in span_raw:
        span_use = str(span_raw["use"])
        inset_raw = span_raw.get("inset", {}) or {}
        if not isinstance(inset_raw, Mapping):
            raise SchemaError("repeat.span.inset must be a mapping")
        inset_start = _resolve_number(inset_raw.get("start", 0.0), dimensions)
        inset_end = _resolve_number(inset_raw.get("end", 0.0), dimensions)
    pitch = _resolve_optional_number(data.get("pitch"), dimensions)
    count_raw = data.get("count")
    count = int(count_raw) if count_raw is not None else None
    include_seed = bool(data.get("include_seed", False))
    return RepeatSpec(
        axis=axis,
        span_use=span_use,
        pitch=pitch,
        count=count,
        inset_start=inset_start,
        inset_end=inset_end,
        include_seed=include_seed,
    )


def _parse_checks(data: Any, dimensions: DimensionResolver) -> List[AlignmentClause]:
    if data is None:
        return []
    if not isinstance(data, Sequence):
        raise SchemaError("checks block must be a list when provided")
    clauses: List[AlignmentClause] = []
    for entry in data:
        if not isinstance(entry, Mapping) or len(entry) != 1:
            raise SchemaError("checks entries must be single-key mappings")
        key = next(iter(entry.keys()))
        if key not in {"align", "contact"}:
            raise SchemaError(f"unsupported check type '{key}'")
        clauses.append(_parse_align_clause(key, entry[key], dimensions))
    return clauses


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
    "AlignmentClause",
    "AssemblyCall",
    "DatumBundle",
    "DatumPlane",
    "DatumPoint",
    "DimensionResolver",
    "FlushBundleClause",
    "InfoBlock",
    "PosToken",
    "RelationshipComponent",
    "RelationshipDiagramSpec",
    "RunBetweenClause",
    "SchemaError",
    "canonical_pos_token",
    "load_relationship_spec",
]
