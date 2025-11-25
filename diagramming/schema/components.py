from __future__ import annotations

import ast
import math
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Literal, Mapping, Optional, Sequence, Tuple

Alignment = Literal[
    "center",
    "north",
    "north_east",
    "east",
    "south_east",
    "south",
    "south_west",
    "west",
    "north_west",
]


_DIRECTION_VECTORS: Dict[str, Tuple[float, float]] = {
    "north": (0.0, -1.0),
    "up": (0.0, -1.0),
    "south": (0.0, 1.0),
    "down": (0.0, 1.0),
    "east": (1.0, 0.0),
    "right": (1.0, 0.0),
    "west": (-1.0, 0.0),
    "left": (-1.0, 0.0),
    "+x": (1.0, 0.0),
    "x+": (1.0, 0.0),
    "-x": (-1.0, 0.0),
    "x-": (-1.0, 0.0),
    "+y": (0.0, 1.0),
    "y+": (0.0, 1.0),
    "-y": (0.0, -1.0),
    "y-": (0.0, -1.0),
}

_VERTICAL_FACE_ALIASES: Dict[str, str] = {
    "top": "top",
    "upper": "top",
    "ceiling": "top",
    "bottom": "bottom",
    "base": "bottom",
    "lower": "bottom",
    "floor": "bottom",
    "centre": "center",
    "center": "center",
    "mid": "center",
    "middle": "center",
}


def _parse_direction(value: object) -> Tuple[float, float]:
    if isinstance(value, str):
        key = value.strip().lower()
        if key not in _DIRECTION_VECTORS:
            raise ValueError(f"unsupported direction '{value}'")
        dx, dy = _DIRECTION_VECTORS[key]
    else:
        raise ValueError("direction must be provided as a string")
    magnitude = math.hypot(dx, dy)
    if magnitude == 0.0:
        raise ValueError("direction must not be zero length")
    return (dx / magnitude, dy / magnitude)


def _resolve_value(
    value: Any, dimensions: Mapping[str, float] | None = None, *, allow_zero: bool = True
) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value_str = value.strip()
        try:
            return float(value_str)
        except ValueError:
            return _evaluate_expression(value_str, dimensions or {})
    raise ValueError(f"expected numeric value or dimension name, got {value!r}")


def _evaluate_expression(expr: str, dimensions: Mapping[str, float]) -> float:
    if not expr:
        raise ValueError("expression cannot be empty")
    try:
        node = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"invalid expression '{expr}': {exc}") from exc
    return _eval_ast(node.body, dimensions)


def _eval_ast(node: ast.AST, dimensions: Mapping[str, float]) -> float:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"unsupported constant {node.value!r} in expression")
    if isinstance(node, ast.Name):
        if node.id not in dimensions:
            raise ValueError(f"unknown dimension '{node.id}' in expression")
        return float(dimensions[node.id])
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        value = _eval_ast(node.operand, dimensions)
        return -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.BinOp) and isinstance(
        node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)
    ):
        left = _eval_ast(node.left, dimensions)
        right = _eval_ast(node.right, dimensions)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
    raise ValueError("only +, -, *, /, unary +/- and dimension names are supported")


def _parse_offset(
    value: Any, dimensions: Mapping[str, float] | None = None
) -> Tuple[float, float]:
    dimensions = dimensions or {}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        if len(value) != 2:
            raise ValueError("offset sequences must have exactly 2 entries")
        return (_resolve_value(value[0], dimensions), _resolve_value(value[1], dimensions))
    if isinstance(value, Mapping):
        dx = 0.0
        dy = 0.0
        for key, raw_amount in value.items():
            amount = _resolve_value(raw_amount, dimensions)
            key_lower = str(key).lower()
            if key_lower in {"east", "right"}:
                dx += amount
            elif key_lower in {"west", "left"}:
                dx -= amount
            elif key_lower in {"south", "down"}:
                dy += amount
            elif key_lower in {"north", "up"}:
                dy -= amount
            elif key_lower in {"x", "dx", "horizontal"}:
                dx += amount
            elif key_lower in {"y", "dy", "vertical"}:
                dy += amount
            else:
                raise ValueError(f"unsupported offset direction '{key}'")
        return (dx, dy)
    raise ValueError("offset must be a 2-sequence or mapping of directions")


def _normalise_anchor_point(
    data: Mapping[str, Any],
    *,
    default: Optional[Alignment] = "center",
) -> Optional[Alignment]:
    for key in (
        "anchor_point",
        "attach",
        "attach_side",
        "attach_point",
        "attach_edge",
        "attach_face",
    ):
        if key in data and data[key] is not None:
            return str(data[key])  # type: ignore[return-value]
    return default


def _iter_moves(
    move_data: Any,
) -> Iterable[Mapping[str, Any]]:
    if move_data is None:
        return ()
    if isinstance(move_data, Mapping):
        return (move_data,)
    if isinstance(move_data, Sequence):
        return tuple(item for item in move_data if item is not None)
    raise ValueError("placement.move must be a mapping or list of mappings")


def _placement_to_anchor(
    data: Mapping[str, Any],
    dimensions: Mapping[str, float] | None = None,
) -> "Anchor":
    dimensions = dimensions or {}
    ref: Optional[str] = None
    align: Optional[Alignment] = None
    flush_edge: Optional[Alignment] = None

    if "flush" in data:
        flush_data = data["flush"]
        if not isinstance(flush_data, Mapping):
            raise ValueError("placement.flush must be a mapping")
        if "edge" not in flush_data:
            raise ValueError("placement.flush requires 'edge'")
        flush_edge = str(flush_data["edge"])  # type: ignore[assignment]
        if "ref" in flush_data:
            ref = str(flush_data["ref"])
        align = flush_edge

    base = data.get("from")
    if base is not None:
        if not isinstance(base, Mapping):
            raise ValueError("placement.from must be a mapping")
        if "ref" in base:
            ref = str(base["ref"])
        if align is None:
            align = base.get("align", "center")  # type: ignore[assignment]

    if ref is None:
        raise ValueError("placement requires 'from.ref' or 'flush.ref'")
    if align is None:
        align = "center"

    attach = _normalise_anchor_point(data, default=None)
    if attach is None:
        attach = flush_edge or "center"

    dx = 0.0
    dy = 0.0
    for move in _iter_moves(data.get("move")):
        direction = move.get("direction")
        if direction:
            direction_lower = str(direction).lower()
            if direction_lower not in _DIRECTION_VECTORS:
                raise ValueError(f"unsupported move direction '{direction}'")
            distance_raw = move.get("distance")
            if distance_raw is None:
                raise ValueError("placement.move requires 'distance' when 'direction' is set")
            distance = _resolve_value(distance_raw, dimensions)
            vector = _DIRECTION_VECTORS[direction_lower]
            dx += vector[0] * distance
            dy += vector[1] * distance
            continue
        if "vector" in move:
            vector_dx, vector_dy = _parse_offset(move["vector"], dimensions)
            dx += vector_dx
            dy += vector_dy
            continue
        raise ValueError("placement.move entries require 'direction' or 'vector'")
    for extra_key in ("offset", "inset"):
        if extra_key in data:
            off_dx, off_dy = _parse_offset(data[extra_key], dimensions)
            dx += off_dx
            dy += off_dy
    return Anchor(
        ref=ref,
        align=align,  # type: ignore[arg-type]
        anchor_point=attach,  # type: ignore[arg-type]
        offset=(dx, dy),
    )


def _normalise_vertical_face(value: Optional[object], *, default: str = "center") -> str:
    if value is None:
        return default
    face_key = str(value).lower()
    if face_key not in _VERTICAL_FACE_ALIASES:
        raise ValueError(f"unsupported vertical face '{value}'")
    return _VERTICAL_FACE_ALIASES[face_key]


def _resolve_vertical_offset(face: str, height: float) -> float:
    if face == "top":
        return height
    if face == "bottom":
        return 0.0
    if face == "center":
        return height / 2.0
    raise ValueError(f"unsupported vertical face '{face}'")


@dataclass(slots=True)
class VerticalPlacement:
    ref: str
    ref_face: str = "center"
    attach_face: str = "center"
    offset: float = 0.0

    @staticmethod
    def from_dict(
        data: Mapping[str, Any],
        *,
        dimensions: Mapping[str, float] | None = None,
    ) -> "VerticalPlacement":
        if not isinstance(data, Mapping):
            raise ValueError("vertical placement must be a mapping")
        dimensions = dimensions or {}

        ref: Optional[str] = None
        ref_face = "center"

        if "flush" in data:
            flush = data["flush"]
            if not isinstance(flush, Mapping):
                raise ValueError("vertical.flush must be a mapping")
            if "face" not in flush:
                raise ValueError("vertical.flush requires 'face'")
            if "ref" in flush:
                ref = str(flush["ref"])
            ref_face = _normalise_vertical_face(flush.get("face"))

        base = data.get("from")
        if base is not None:
            if not isinstance(base, Mapping):
                raise ValueError("vertical.from must be a mapping")
            if "ref" in base:
                ref = str(base["ref"])
            if "face" in base:
                ref_face = _normalise_vertical_face(base.get("face"))

        if "ref" in data:
            ref = str(data["ref"])
        if ref is None:
            raise ValueError("vertical placement requires a 'ref'")

        attach_face = _normalise_vertical_face(
            data.get("attach_face") or data.get("attach") or data.get("anchor_face"),
            default=ref_face,
        )
        offset = _resolve_value(data.get("offset", 0.0), dimensions)

        return VerticalPlacement(
            ref=ref,
            ref_face=ref_face,
            attach_face=attach_face,
            offset=offset,
        )

    def resolve(self, ref_elevation: float, ref_height: float, self_height: float) -> float:
        ref_face_value = ref_elevation + _resolve_vertical_offset(self.ref_face, ref_height)
        attach_offset = _resolve_vertical_offset(self.attach_face, self_height)
        return ref_face_value - attach_offset + self.offset


@dataclass(slots=True)
class Anchor:
    ref: str
    align: Alignment = "center"
    anchor_point: Alignment = "center"
    offset: Tuple[float, float] = (0.0, 0.0)

    @staticmethod
    def from_dict(data: dict, *, dimensions: Mapping[str, float] | None = None) -> "Anchor":
        if "ref" not in data:
            raise ValueError("anchor requires a 'ref' field")
        align = data.get("align", "center")
        anchor_point = _normalise_anchor_point(data)
        offset_raw = data.get("offset", (0.0, 0.0))
        offset = _parse_offset(offset_raw, dimensions)
        return Anchor(
            ref=str(data["ref"]),
            align=align,  # type: ignore[arg-type]
            anchor_point=anchor_point,  # type: ignore[arg-type]
            offset=offset,
        )


@dataclass(slots=True)
class Repeat:
    count: int
    spacing: Tuple[float, float]
    include_base: bool = True
    label_suffix: Optional[str] = None
    rotate: float = 0.0
    about: Optional[Anchor] = None
    interval: Optional[float] = None
    span: Optional[float] = None
    direction: Optional[Tuple[float, float]] = None
    span_mode: str = "inclusive"

    @staticmethod
    def from_dict(data: dict, *, dimensions: Mapping[str, float] | None = None) -> "Repeat":
        dimensions = dimensions or {}
        count_raw = data.get("count")
        count: Optional[int] = None
        if count_raw is not None:
            count = int(count_raw)
            if count <= 0:
                raise ValueError("repeat.count must be positive")
        spacing_raw = data.get("spacing")
        if spacing_raw is None:
            spacing: Optional[Tuple[float, float]] = None
        elif not isinstance(spacing_raw, Sequence) or len(spacing_raw) != 2:
            raise ValueError("repeat.spacing must be a 2-element sequence")
        else:
            spacing = (
                _resolve_value(spacing_raw[0], dimensions),
                _resolve_value(spacing_raw[1], dimensions),
            )
        interval_raw = data.get("interval")
        interval = (
            _resolve_value(interval_raw, dimensions) if interval_raw is not None else None
        )
        span_raw = data.get("span")
        span = _resolve_value(span_raw, dimensions) if span_raw is not None else None
        span_mode = str(data.get("span_mode", "inclusive")).lower()
        if span_mode not in ("inclusive", "exclusive"):
            raise ValueError("repeat.span_mode must be 'inclusive' or 'exclusive'")
        direction_vector: Optional[Tuple[float, float]] = None
        if "vector" in data:
            vector_raw = data["vector"]
            if not isinstance(vector_raw, Sequence) or len(vector_raw) != 2:
                raise ValueError("repeat.vector must be a 2-element sequence")
            dx = _resolve_value(vector_raw[0], dimensions)
            dy = _resolve_value(vector_raw[1], dimensions)
            magnitude = math.hypot(dx, dy)
            if magnitude == 0.0:
                raise ValueError("repeat.vector must not be zero length")
            direction_vector = (dx / magnitude, dy / magnitude)
        elif "direction" in data:
            direction_vector = _parse_direction(data["direction"])
        include_base = bool(data.get("include_base", True))
        label_suffix = data.get("label_suffix")
        if label_suffix is not None:
            label_suffix = str(label_suffix)
        rotate_value = float(data.get("rotate", 0.0))
        about_anchor = data.get("about")
        about = (
            Anchor.from_dict(about_anchor, dimensions=dimensions)
            if isinstance(about_anchor, Mapping)
            else None
        )
        if spacing is not None and spacing == (0.0, 0.0):
            spacing = None

        if spacing is None:
            if interval is not None:
                if direction_vector is None:
                    raise ValueError("repeat.interval requires 'direction' or 'vector'")
                if interval <= 0.0:
                    raise ValueError("repeat.interval must be positive")
                if span is not None:
                    computed = int(math.floor(span / interval + 1e-9)) + 1
                    if computed <= 0:
                        raise ValueError("repeat.span/interval combination produced no instances")
                    if count is None:
                        count = computed
                    elif count != computed:
                        raise ValueError(
                            "repeat.count does not match the derived span/interval combination"
                        )
                spacing = (direction_vector[0] * interval, direction_vector[1] * interval)
            elif span is not None and direction_vector is not None and count is not None:
                if count <= 1:
                    raise ValueError("repeat.span requires count greater than 1")
                divisor = count - 1 if span_mode == "inclusive" else count
                if divisor <= 0:
                    raise ValueError("repeat.span cannot distribute with the given count")
                interval = span / divisor
                spacing = (direction_vector[0] * interval, direction_vector[1] * interval)
            elif direction_vector is not None and count is None:
                raise ValueError(
                    "repeat requires 'interval' or 'span' in combination with 'direction'"
                )

        if spacing is None and rotate_value == 0.0:
            raise ValueError("repeat requires spacing, interval/span, or rotation")

        if spacing == (0.0, 0.0) and rotate_value == 0.0:
            raise ValueError("repeat requires non-zero spacing or rotation")

        if count is None:
            raise ValueError("repeat requires 'count' unless both 'span' and 'interval' are provided")

        return Repeat(
            count=count,
            spacing=spacing,
            include_base=include_base,
            label_suffix=label_suffix,
            rotate=rotate_value,
            about=about,
            interval=interval,
            span=span,
            direction=direction_vector,
            span_mode=span_mode,
        )


@dataclass(slots=True)
class Cutout:
    size: Tuple[float, float]
    anchor: Anchor

    @staticmethod
    def from_dict(data: dict, *, dimensions: Mapping[str, float] | None = None) -> "Cutout":
        if "size" not in data:
            raise ValueError("cutout requires 'size'")
        size_raw = data["size"]
        if not isinstance(size_raw, Sequence) or len(size_raw) != 2:
            raise ValueError("cutout.size must be a 2-element sequence")
        anchor = Anchor.from_dict(data.get("anchor", {"ref": "self"}), dimensions=dimensions)
        return Cutout(
            size=(
                _resolve_value(size_raw[0], dimensions),
                _resolve_value(size_raw[1], dimensions),
            ),
            anchor=anchor,
        )


@dataclass(slots=True)
class BooleanTarget:
    target: str
    include_generated: bool = True

    @staticmethod
    def from_raw(raw: object) -> "BooleanTarget":
        if isinstance(raw, str):
            return BooleanTarget(target=raw, include_generated=True)
        if isinstance(raw, Mapping):
            if "target" not in raw:
                raise ValueError("boolean target mapping requires 'target'")
            include_generated = bool(raw.get("include_generated", True))
            target_raw = raw["target"]
            if not isinstance(target_raw, str):
                raise ValueError("boolean target 'target' must be a string")
            return BooleanTarget(target=target_raw, include_generated=include_generated)
        raise ValueError("boolean targets must be strings or mappings with 'target'")


@dataclass(slots=True)
class BooleanConfig:
    subtract: Tuple[BooleanTarget, ...] = ()

    @staticmethod
    def from_dict(data: Mapping[str, object]) -> "BooleanConfig":
        subtract_raw = data.get("subtract", ())
        if isinstance(subtract_raw, (str, Mapping)):
            subtract_iterable = (subtract_raw,)
        else:
            if not isinstance(subtract_raw, Sequence):
                raise ValueError("boolean.subtract must be a string, mapping, or sequence")
            subtract_iterable = subtract_raw
        subtract: List[BooleanTarget] = [
            BooleanTarget.from_raw(item) for item in subtract_iterable
        ]
        return BooleanConfig(subtract=tuple(subtract))


@dataclass(slots=True)
class IfcPset:
    name: str
    props: Dict[str, Any]


@dataclass(slots=True)
class IfcMetadata:
    predefined_type: Optional[str] = None
    psets: Tuple[IfcPset, ...] = ()

    @staticmethod
    def from_dict(data: Mapping[str, object]) -> "IfcMetadata":
        predefined_raw = data.get("predefined_type")
        predefined_type = str(predefined_raw).upper() if predefined_raw is not None else None
        psets_raw = data.get("psets", ())
        psets: List[IfcPset] = []
        if psets_raw:
            if not isinstance(psets_raw, Sequence):
                raise ValueError("ifc.psets must be a list when provided")
            for item in psets_raw:
                if not isinstance(item, Mapping):
                    raise ValueError("ifc.psets entries must be mappings")
                if "name" not in item or "props" not in item:
                    raise ValueError("ifc.psets entries require 'name' and 'props'")
                props = item.get("props")
                if not isinstance(props, Mapping):
                    raise ValueError("ifc.psets.props must be a mapping")
                psets.append(IfcPset(name=str(item["name"]), props=dict(props)))
        return IfcMetadata(predefined_type=predefined_type, psets=tuple(psets))

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        if self.predefined_type is not None:
            data["predefined_type"] = self.predefined_type
        if self.psets:
            data["psets"] = [{"name": pset.name, "props": pset.props} for pset in self.psets]
        return data


@dataclass(slots=True)
class ComponentBase:
    id: str
    label: Optional[str] = None
    label_id: Optional[str] = None
    class_name: Optional[str] = None
    material: Optional[str] = None
    views: Tuple[str, ...] = ("plan",)
    height: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    traits: Tuple[str, ...] = ()
    rotation: float = 0.0
    rotation_anchor: Optional[Anchor] = None
    vertical: Optional[VerticalPlacement] = None
    ifc: Optional["IfcMetadata"] = None


@dataclass(slots=True)
class RectangleComponent(ComponentBase):
    size: Tuple[float, float] = (0.0, 0.0)
    origin: Optional[Tuple[float, float]] = None
    anchor: Optional[Anchor] = None
    repeat: Optional[Repeat] = None
    cutouts: List[Cutout] = field(default_factory=list)
    boolean: Optional[BooleanConfig] = None

    @staticmethod
    def from_dict(
        data: dict,
        *,
        dimensions: Mapping[str, float] | None = None,
    ) -> "RectangleComponent":
        if "id" not in data:
            raise ValueError("rectangle requires an 'id'")
        if "size" not in data:
            raise ValueError(f"rectangle '{data['id']}' requires 'size'")
        size_raw = data["size"]
        if not isinstance(size_raw, Sequence) or len(size_raw) != 2:
            raise ValueError(f"rectangle '{data['id']}' size must have 2 entries")
        origin = None
        if "origin" in data:
            origin_raw = data["origin"]
            if not isinstance(origin_raw, Sequence) or len(origin_raw) != 2:
                raise ValueError(f"rectangle '{data['id']}' origin must have 2 entries")
            origin = (
                _resolve_value(origin_raw[0], dimensions),
                _resolve_value(origin_raw[1], dimensions),
            )
        anchor = (
            Anchor.from_dict(data["anchor"], dimensions=dimensions) if "anchor" in data else None
        )
        if "placement" in data:
            if origin is not None:
                raise ValueError("rectangle cannot specify both 'origin' and 'placement'")
            if anchor is not None:
                raise ValueError("rectangle cannot specify both 'anchor' and 'placement'")
            placement_data = data["placement"]
            if not isinstance(placement_data, Mapping):
                raise ValueError("placement must be a mapping")
            anchor = _placement_to_anchor(placement_data, dimensions)
        repeat = (
            Repeat.from_dict(data["repeat"], dimensions=dimensions) if "repeat" in data else None
        )
        cutouts_data = data.get("cutouts", [])
        cutouts = [Cutout.from_dict(item, dimensions=dimensions) for item in cutouts_data]
        views_data = data.get("views")
        if views_data is None:
            views: Tuple[str, ...] = ("plan",)
        elif isinstance(views_data, str):
            views = (views_data,)
        else:
            views = tuple(str(v) for v in views_data)
        metadata = _parse_metadata(data.get("metadata"), dimensions)
        traits = _parse_traits(data.get("traits"))
        height = _resolve_value(data["height"], dimensions) if "height" in data else None
        rotation = float(data.get("rotation", 0.0))
        rotation_anchor = (
            Anchor.from_dict(data["rotation_anchor"], dimensions=dimensions)
            if "rotation_anchor" in data and isinstance(data["rotation_anchor"], Mapping)
            else None
        )
        boolean_config = None
        if "boolean" in data:
            boolean_raw = data["boolean"]
            if not isinstance(boolean_raw, Mapping):
                raise ValueError("boolean configuration must be a mapping")
            boolean_config = BooleanConfig.from_dict(boolean_raw)
        vertical = (
            VerticalPlacement.from_dict(data["vertical"], dimensions=dimensions)
            if "vertical" in data and isinstance(data["vertical"], Mapping)
            else None
        )
        ifc = None
        if "ifc" in data:
            ifc_raw = data["ifc"]
            if not isinstance(ifc_raw, Mapping):
                raise ValueError("ifc block must be a mapping")
            ifc = IfcMetadata.from_dict(ifc_raw)
        return RectangleComponent(
            id=str(data["id"]),
            label=data.get("label"),
            label_id=data.get("label_id"),
            class_name=data.get("class"),
            material=data.get("material"),
            views=views,
            size=(
                _resolve_value(size_raw[0], dimensions),
                _resolve_value(size_raw[1], dimensions),
            ),
            origin=origin,
            anchor=anchor,
            repeat=repeat,
            cutouts=cutouts,
            boolean=boolean_config,
            height=height,
            metadata=metadata,
            traits=traits,
            rotation=rotation,
            rotation_anchor=rotation_anchor,
            vertical=vertical,
            ifc=ifc,
        )


@dataclass(slots=True)
class PolylineComponent(ComponentBase):
    points: Tuple[Tuple[float, float], ...] = ()
    origin: Optional[Tuple[float, float]] = None
    anchor: Optional[Anchor] = None
    stroke_width: float = 2.0

    @staticmethod
    def from_dict(
        data: dict,
        *,
        dimensions: Mapping[str, float] | None = None,
    ) -> "PolylineComponent":
        if "id" not in data:
            raise ValueError("polyline requires an 'id'")
        points_raw = data.get("points")
        if not points_raw:
            raise ValueError(f"polyline '{data['id']}' requires 'points'")
        points: List[Tuple[float, float]] = []
        for pt in points_raw:
            if not isinstance(pt, Sequence) or len(pt) != 2:
                raise ValueError(f"polyline '{data['id']}' point must have 2 entries")
            points.append(
                (_resolve_value(pt[0], dimensions), _resolve_value(pt[1], dimensions))
            )
        origin = None
        if "origin" in data:
            origin_raw = data["origin"]
            if not isinstance(origin_raw, Sequence) or len(origin_raw) != 2:
                raise ValueError(f"polyline '{data['id']}' origin must have 2 entries")
            origin = (
                _resolve_value(origin_raw[0], dimensions),
                _resolve_value(origin_raw[1], dimensions),
            )
        anchor = (
            Anchor.from_dict(data["anchor"], dimensions=dimensions) if "anchor" in data else None
        )
        if "placement" in data:
            if origin is not None:
                raise ValueError("polyline cannot specify both 'origin' and 'placement'")
            if anchor is not None:
                raise ValueError("polyline cannot specify both 'anchor' and 'placement'")
            placement_data = data["placement"]
            if not isinstance(placement_data, Mapping):
                raise ValueError("placement must be a mapping")
            anchor = _placement_to_anchor(placement_data, dimensions)
        views_data = data.get("views")
        if views_data is None:
            views: Tuple[str, ...] = ("plan",)
        elif isinstance(views_data, str):
            views = (views_data,)
        else:
            views = tuple(str(v) for v in views_data)
        stroke_width = float(data.get("stroke_width", 2.0))
        metadata = _parse_metadata(data.get("metadata"), dimensions)
        traits = _parse_traits(data.get("traits"))
        height = _resolve_value(data["height"], dimensions) if "height" in data else None
        rotation = float(data.get("rotation", 0.0))
        rotation_anchor = (
            Anchor.from_dict(data["rotation_anchor"], dimensions=dimensions)
            if "rotation_anchor" in data and isinstance(data["rotation_anchor"], Mapping)
            else None
        )
        vertical = (
            VerticalPlacement.from_dict(data["vertical"], dimensions=dimensions)
            if "vertical" in data and isinstance(data["vertical"], Mapping)
            else None
        )
        ifc = None
        if "ifc" in data:
            ifc_raw = data["ifc"]
            if not isinstance(ifc_raw, Mapping):
                raise ValueError("ifc block must be a mapping")
            ifc = IfcMetadata.from_dict(ifc_raw)
        return PolylineComponent(
            id=str(data["id"]),
            label=data.get("label"),
            label_id=data.get("label_id"),
            class_name=data.get("class"),
            material=data.get("material"),
            views=views,
            points=tuple(points),
            origin=origin,
            anchor=anchor,
            stroke_width=stroke_width,
            height=height,
            metadata=metadata,
            traits=traits,
            rotation=rotation,
            rotation_anchor=rotation_anchor,
            vertical=vertical,
            ifc=ifc,
        )


Component = RectangleComponent | PolylineComponent
def _parse_metadata(
    raw: object,
    dimensions: Mapping[str, float] | None = None,
) -> Dict[str, Any]:
    if raw is None:
        return {}
    if not isinstance(raw, Mapping):
        raise ValueError("component metadata must be a mapping")
    metadata: Dict[str, Any] = {}
    dimensions = dimensions or {}
    for key, value in raw.items():
        str_key = str(key)
        if isinstance(value, Mapping):
            metadata[str_key] = _parse_metadata(value, dimensions)
            continue
        if isinstance(value, (int, float)):
            metadata[str_key] = float(value)
            continue
        if isinstance(value, str):
            try:
                metadata[str_key] = _resolve_value(value, dimensions)
            except ValueError:
                metadata[str_key] = value
            continue
        metadata[str_key] = value
    return metadata


def _parse_traits(raw: object) -> Tuple[str, ...]:
    if raw is None:
        return ()
    if isinstance(raw, (str, bytes)):
        raise ValueError("traits must be provided as a list, not a string")
    if not isinstance(raw, Sequence):
        raise ValueError("traits must be a sequence of strings")
    return tuple(str(item) for item in raw)
