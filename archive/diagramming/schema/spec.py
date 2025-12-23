from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Set, Tuple

import yaml

from .components import Anchor, Component, PolylineComponent, RectangleComponent, _resolve_value


@dataclass(slots=True)
class PlaneSpec:
    axis: str
    coordinate: float


@dataclass(slots=True)
class ViewSpec:
    name: str
    title: Optional[str] = None
    aria_label: Optional[str] = None
    pad: float = 48.0
    class_name: Optional[str] = None
    scale: Optional[float] = None
    background: Optional[str] = None
    plane: Optional[PlaneSpec] = None


@dataclass(slots=True)
class OptionSpec:
    key: str
    title: str
    components: List[Component] = field(default_factory=list)
    views: Dict[str, ViewSpec] = field(default_factory=dict)
    notes: Optional[str] = None
    operations: List["Operation"] = field(default_factory=list)
    dimensions: Dict[str, float] = field(default_factory=dict)

    def components_for_view(self, view_name: str) -> List[Component]:
        return [
            component
            for component in self.components
            if view_name in getattr(component, "views", ("plan",))
        ]

    def view_names(self) -> List[str]:
        names = set(self.views.keys())
        for component in self.components:
            for view_name in getattr(component, "views", ("plan",)):
                names.add(view_name)
        return sorted(names)


@dataclass(slots=True)
class DiagramSpec:
    name: str
    units: str = "mm"
    scale: Optional[float] = None
    options: Dict[str, OptionSpec] = field(default_factory=dict)

    def option_keys(self) -> Iterable[str]:
        return self.options.keys()

    def get_option(self, key: str) -> OptionSpec:
        if key not in self.options:
            raise KeyError(f"option '{key}' not found in spec '{self.name}'")
        return self.options[key]


def _parse_component(data: Mapping[str, object], *, dimensions: Mapping[str, float]) -> Component:
    component_type = data.get("type")
    if component_type == "rectangle":
        return RectangleComponent.from_dict(dict(data), dimensions=dimensions)
    if component_type == "polyline":
        return PolylineComponent.from_dict(dict(data), dimensions=dimensions)
    raise ValueError(f"unknown component type: {component_type!r}")


@dataclass(slots=True)
class Operation:
    type: str


@dataclass(slots=True)
class RotateOperation(Operation):
    type: str = "rotate"
    targets: Tuple[str, ...] = ()
    count: int = 0
    angle: float = 0.0
    include_base: bool = True
    about: Optional[Anchor] = None
    include_generated: bool = False


@dataclass(slots=True)
class MirrorOperation(Operation):
    type: str = "mirror"
    targets: Tuple[str, ...] = ()
    axis: str = "y"
    about: Optional[Anchor] = None
    include_generated: bool = False


def _parse_operation(data: Mapping[str, object]) -> Operation:
    operation_type = data.get("type")
    if operation_type == "rotate":
        targets_raw = data.get("targets")
        if targets_raw is None:
            raise ValueError("rotate operation requires 'targets'")
        if isinstance(targets_raw, (str, bytes)):
            targets = (str(targets_raw),)
        elif isinstance(targets_raw, Sequence):
            targets = tuple(str(item) for item in targets_raw)
        else:
            raise ValueError("rotate operation 'targets' must be a string or sequence of strings")
        if not targets:
            raise ValueError("rotate operation requires at least one target")
        count_raw = data.get("count")
        if count_raw is None:
            raise ValueError("rotate operation requires 'count'")
        count = int(count_raw)
        if count <= 0:
            raise ValueError("rotate operation 'count' must be positive")
        angle = float(data.get("angle", 0.0))
        if angle == 0.0:
            raise ValueError("rotate operation requires non-zero 'angle'")
        include_base = bool(data.get("include_base", True))
        include_generated = bool(data.get("include_generated", False))
        about_raw = data.get("about")
        about = Anchor.from_dict(about_raw) if isinstance(about_raw, Mapping) else None
        return RotateOperation(
            targets=targets,
            count=count,
            angle=angle,
            include_base=include_base,
            about=about,
            include_generated=include_generated,
        )
    if operation_type == "mirror":
        targets_raw = data.get("targets")
        if targets_raw is None:
            raise ValueError("mirror operation requires 'targets'")
        if isinstance(targets_raw, (str, bytes)):
            targets = (str(targets_raw),)
        elif isinstance(targets_raw, Sequence):
            targets = tuple(str(item) for item in targets_raw)
        else:
            raise ValueError("mirror operation 'targets' must be a string or sequence of strings")
        if not targets:
            raise ValueError("mirror operation requires at least one target")
        axis_raw = data.get("axis", "y")
        axis_key = str(axis_raw).lower()
        if axis_key in ("y", "vertical"):
            axis = "y"
        elif axis_key in ("x", "horizontal"):
            axis = "x"
        else:
            raise ValueError("mirror operation 'axis' must be 'x'/'horizontal' or 'y'/'vertical'")
        include_generated = bool(data.get("include_generated", False))
        about_raw = data.get("about")
        about = Anchor.from_dict(about_raw) if isinstance(about_raw, Mapping) else None
        return MirrorOperation(
            targets=targets,
            axis=axis,
            about=about,
            include_generated=include_generated,
        )
    raise ValueError(f"unknown operation type: {operation_type!r}")


def _parse_option(key: str, data: MutableMapping[str, object]) -> OptionSpec:
    title = data.get("title")
    if not isinstance(title, str):
        raise ValueError(f"option '{key}' requires a title")
    dimensions_raw = data.get("dimensions", {})
    if dimensions_raw is None:
        dimensions_raw = {}
    if not isinstance(dimensions_raw, Mapping):
        raise ValueError(f"option '{key}' dimensions must be a mapping when provided")
    dimensions: Dict[str, float] = {}
    for dim_key, dim_value in dimensions_raw.items():
        dimensions[str(dim_key)] = _resolve_value(dim_value, dimensions)
    components_data = data.get("components", [])
    if not isinstance(components_data, list):
        raise ValueError(f"option '{key}' components must be a list")
    components: List[Component] = [
        _parse_component(item, dimensions=dimensions) for item in components_data
    ]

    views_raw = data.get("views", {})
    if not isinstance(views_raw, Mapping):
        raise ValueError(f"option '{key}' views must be a mapping")
    views: Dict[str, ViewSpec] = {}
    for view_name, view_data in views_raw.items():
        if not isinstance(view_data, Mapping):
            raise ValueError(f"view '{view_name}' for option '{key}' must be a mapping")
        view_scale = view_data.get("scale")
        scale_value = float(view_scale) if view_scale is not None else None
        background = view_data.get("background")
        if background is not None:
            background = str(background)
        plane_spec = None
        plane_data = view_data.get("plane")
        if plane_data is not None:
            if not isinstance(plane_data, Mapping):
                raise ValueError(f"view '{view_name}' for option '{key}' plane must be a mapping")
            axis = plane_data.get("axis")
            if axis not in {"x", "y"}:
                raise ValueError(f"view '{view_name}' for option '{key}' plane axis must be 'x' or 'y'")
            coordinate_raw = plane_data.get("coordinate")
            if coordinate_raw is None:
                raise ValueError(f"view '{view_name}' for option '{key}' plane requires 'coordinate'")
            plane_spec = PlaneSpec(axis=str(axis), coordinate=float(coordinate_raw))

        views[view_name] = ViewSpec(
            name=view_name,
            title=view_data.get("title"),
            aria_label=view_data.get("aria_label"),
            pad=float(view_data.get("pad", 48.0)),
            class_name=view_data.get("class"),
            scale=scale_value,
            background=background,
            plane=plane_spec,
        )

    operations_raw = data.get("operations", [])
    if not isinstance(operations_raw, Sequence):
        raise ValueError(f"option '{key}' operations must be a list when provided")
    operations: List[Operation] = []
    for item in operations_raw:
        if not isinstance(item, Mapping):
            raise ValueError(f"option '{key}' operations entries must be mappings")
        operations.append(_parse_operation(item))

    notes = data.get("notes")
    _validate_option_components(key, components)
    return OptionSpec(
        key=key,
        title=title,
        components=components,
        views=views,
        notes=notes,
        operations=operations,
        dimensions=dimensions,
    )  # type: ignore[arg-type]


def load_spec(
    path: Path | str,
    *,
    include_options: Optional[Iterable[str]] = None,
) -> DiagramSpec:
    path = Path(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, MutableMapping):
        raise ValueError("spec root must be a mapping")
    name = raw.get("name") or path.stem
    name = str(name)
    units = str(raw.get("units", "mm"))
    scale_raw = raw.get("scale")
    scale = float(scale_raw) if scale_raw is not None else None
    options_raw = raw.get("options")
    if not isinstance(options_raw, Mapping) or not options_raw:
        raise ValueError("spec requires at least one option")
    option_filter: Optional[Set[str]] = None
    if include_options:
        option_filter = {str(option_key) for option_key in include_options}
    options: Dict[str, OptionSpec] = {}
    for key, value in options_raw.items():
        key_str = str(key)
        if option_filter is not None and key_str not in option_filter:
            continue
        if not isinstance(value, MutableMapping):
            raise ValueError(f"option '{key}' must be a mapping")
        options[key_str] = _parse_option(key_str, value)
    if option_filter is not None:
        missing = option_filter.difference(options.keys())
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise ValueError(f"spec '{name}' is missing requested option(s): {missing_list}")
        if not options:
            raise ValueError(f"spec '{name}' did not load any of the requested options")
    return DiagramSpec(name=name, units=units, scale=scale, options=options)


def _validate_option_components(option_key: str, components: List[Component]) -> None:
    ids: set[str] = set()
    for component in components:
        if component.id in ids:
            raise ValueError(f"option '{option_key}' has duplicate component id '{component.id}'")
        ids.add(component.id)

    def ensure_anchor(ref: str, owner_id: str) -> None:
        if ref == "self":
            return
        if ref not in ids:
            raise ValueError(
                f"option '{option_key}' component '{owner_id}' references unknown anchor '{ref}'"
            )

    for component in components:
        anchor = getattr(component, "anchor", None)
        if anchor is not None:
            ensure_anchor(anchor.ref, component.id)

        if isinstance(component, RectangleComponent):
            for cutout in component.cutouts:
                ensure_anchor(cutout.anchor.ref, f"{component.id} cutout")
            if component.boolean:
                for target in component.boolean.subtract:
                    if target.target not in ids:
                        raise ValueError(
                            f"option '{option_key}' component '{component.id}' boolean subtract references unknown component '{target.target}'"
                        )

        if isinstance(component, PolylineComponent):
            # already covered by generic anchor check; kept for clarity & future extension
            continue
