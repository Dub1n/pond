from __future__ import annotations

from typing import Tuple

from .core import SvgScene, _fmt


def horizontal_dimension(
    scene: SvgScene,
    x0: float,
    x1: float,
    reference_y: float,
    label: str,
    direction: str = "down",
    offset: float = 36.0,
    extension: float = 16.0,
    text_offset: float | None = None,
    label_anchor: str = "middle",
) -> None:
    """
    Draw a horizontal (X-axis) dimension with extension lines projected from reference_y.
    direction: 'down' -> dimension line below geometry, 'up' -> above.
    """
    if x0 > x1:
        x0, x1 = x1, x0
    arrow = scene.ensure_arrow_marker()
    if direction not in {"down", "up"}:
        raise ValueError("direction must be 'down' or 'up'")
    sign = 1 if direction == "down" else -1
    dim_y = reference_y + sign * offset
    ext_end = dim_y + sign * extension
    scene.line(x0, reference_y, x0, ext_end, class_="dim-extension")
    scene.line(x1, reference_y, x1, ext_end, class_="dim-extension")
    scene.line(
        x0,
        dim_y,
        x1,
        dim_y,
        class_="dim-line",
        marker_start=arrow,
        marker_end=arrow,
    )
    if text_offset is None:
        text_offset = -sign * (offset * 0.4 + 6)
    scene.text(
        (x0 + x1) / 2,
        dim_y + text_offset,
        label,
        anchor=label_anchor,
        class_="dim-text",
    )


def vertical_dimension(
    scene: SvgScene,
    y0: float,
    y1: float,
    reference_x: float,
    label: str,
    direction: str = "right",
    offset: float = 36.0,
    extension: float = 16.0,
    text_offset: float | None = None,
    label_anchor: str = "middle",
) -> None:
    """
    Draw a vertical (Y-axis) dimension with extension lines projected from reference_x.
    direction: 'right' -> dimension line right of geometry, 'left' -> left.
    """
    if y0 > y1:
        y0, y1 = y1, y0
    arrow = scene.ensure_arrow_marker()
    if direction not in {"right", "left"}:
        raise ValueError("direction must be 'left' or 'right'")
    sign = 1 if direction == "right" else -1
    dim_x = reference_x + sign * offset
    ext_end = dim_x + sign * extension
    scene.line(reference_x, y0, ext_end, y0, class_="dim-extension")
    scene.line(reference_x, y1, ext_end, y1, class_="dim-extension")
    scene.line(
        dim_x,
        y0,
        dim_x,
        y1,
        class_="dim-line",
        marker_start=arrow,
        marker_end=arrow,
    )
    if text_offset is None:
        text_offset = -sign * (offset * 0.4 + 6)
    scene.text(
        dim_x + text_offset,
        (y0 + y1) / 2,
        label,
        anchor=label_anchor,
        class_="dim-text",
        transform=f"rotate(-90 {dim_x + text_offset},{(y0 + y1) / 2})",
    )

