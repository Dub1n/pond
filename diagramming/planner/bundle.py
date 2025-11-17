from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - import hints only
    from shapely.geometry import LineString, Polygon
    import trimesh


@dataclass(slots=True)
class LegendEntry:
    label: str
    label_id: Optional[str] = None


@dataclass(slots=True)
class PolygonFeature:
    id: str
    outer: Sequence[Tuple[float, float]]
    holes: Sequence[Sequence[Tuple[float, float]]] = ()
    label: Optional[str] = None
    label_id: Optional[str] = None
    class_name: Optional[str] = None
    height: float = 0.0
    elevation: float = 0.0
    material: Optional[str] = None
    metadata: Dict[str, object] = field(default_factory=dict)
    shape: Optional["Polygon"] = None
    views: Tuple[str, ...] = ("plan",)


@dataclass(slots=True)
class PolylineFeature:
    id: str
    points: Sequence[Tuple[float, float]]
    stroke_width: float = 2.0
    label: Optional[str] = None
    label_id: Optional[str] = None
    class_name: Optional[str] = None
    elevation: float = 0.0
    thickness: float = 0.0
    material: Optional[str] = None
    metadata: Dict[str, object] = field(default_factory=dict)
    shape: Optional["LineString"] = None
    views: Tuple[str, ...] = ("plan",)


@dataclass(slots=True)
class GeometryBundle:
    view: str
    polygons: List[PolygonFeature] = field(default_factory=list)
    polylines: List[PolylineFeature] = field(default_factory=list)
    legend: List[LegendEntry] = field(default_factory=list)
    pad: float = 48.0
    scale: float = 1.0
    background: Optional[str] = None
    scene: Optional["trimesh.Scene"] = None

    def add_polygon(self, feature: PolygonFeature) -> None:
        self.polygons.append(feature)

    def add_polyline(self, feature: PolylineFeature) -> None:
        self.polylines.append(feature)

    def build_legend(self) -> None:
        seen: set[tuple[str, Optional[str]]] = set()
        entries: List[LegendEntry] = []
        for feature in self.polygons:
            if not feature.label:
                continue
            key = (feature.label, feature.label_id)
            if key in seen:
                continue
            seen.add(key)
            entries.append(LegendEntry(label=feature.label, label_id=feature.label_id))
        for feature in self.polylines:
            if not feature.label:
                continue
            key = (feature.label, feature.label_id)
            if key in seen:
                continue
            seen.add(key)
            entries.append(LegendEntry(label=feature.label, label_id=feature.label_id))
        self.legend = entries

    def extent(self) -> Optional[Tuple[float, float, float, float]]:
        xs: List[float] = []
        ys: List[float] = []
        for feature in self.polygons:
            for x, y in feature.outer:
                xs.append(x)
                ys.append(y)
            for hole in feature.holes:
                for x, y in hole:
                    xs.append(x)
                    ys.append(y)
        for feature in self.polylines:
            for x, y in feature.points:
                xs.append(x)
                ys.append(y)
        if not xs or not ys:
            return None
        return (min(xs), min(ys), max(xs), max(ys))
