from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple

from ..schema.components import Alignment


@dataclass(frozen=True)
class Bounds:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_y - self.min_y

    def point(self, alignment: Alignment) -> Tuple[float, float]:
        if alignment == "center":
            return ((self.min_x + self.max_x) / 2, (self.min_y + self.max_y) / 2)
        if alignment == "north":
            return ((self.min_x + self.max_x) / 2, self.min_y)
        if alignment == "north_east":
            return (self.max_x, self.min_y)
        if alignment == "east":
            return (self.max_x, (self.min_y + self.max_y) / 2)
        if alignment == "south_east":
            return (self.max_x, self.max_y)
        if alignment == "south":
            return ((self.min_x + self.max_x) / 2, self.max_y)
        if alignment == "south_west":
            return (self.min_x, self.max_y)
        if alignment == "west":
            return (self.min_x, (self.min_y + self.max_y) / 2)
        if alignment == "north_west":
            return (self.min_x, self.min_y)
        raise ValueError(f"unknown alignment '{alignment}'")


def alignment_offset(size: Tuple[float, float], alignment: Alignment) -> Tuple[float, float]:
    width, height = size
    if alignment == "center":
        return (width / 2, height / 2)
    if alignment == "north":
        return (width / 2, 0.0)
    if alignment == "north_east":
        return (width, 0.0)
    if alignment == "east":
        return (width, height / 2)
    if alignment == "south_east":
        return (width, height)
    if alignment == "south":
        return (width / 2, height)
    if alignment == "south_west":
        return (0.0, height)
    if alignment == "west":
        return (0.0, height / 2)
    if alignment == "north_west":
        return (0.0, 0.0)
    raise ValueError(f"unknown alignment '{alignment}'")


def rect_to_bounds(points: Sequence[Tuple[float, float]]) -> Bounds:
    xs = [pt[0] for pt in points]
    ys = [pt[1] for pt in points]
    return Bounds(min_x=min(xs), min_y=min(ys), max_x=max(xs), max_y=max(ys))


def create_rectangle(top_left: Tuple[float, float], size: Tuple[float, float]) -> Tuple[
    Tuple[float, float], ...
]:
    x, y = top_left
    width, height = size
    return (
        (x, y),
        (x + width, y),
        (x + width, y + height),
        (x, y + height),
        (x, y),
    )


def bounds_from_origin(top_left: Tuple[float, float], size: Tuple[float, float]) -> Bounds:
    x, y = top_left
    width, height = size
    return Bounds(min_x=x, min_y=y, max_x=x + width, max_y=y + height)
