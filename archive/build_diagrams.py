#!/usr/bin/env python3
"""
Build all SVG diagrams from the YAML specs in diagrams/specs/.

Usage:
  python scripts/build_diagrams.py [--spec path.yaml ...] [--outdir diagrams/output]
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Dict, Iterable, Mapping, Optional

import yaml

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from diagramming.attachments import AttachmentOption, render_attachment_diagram
from diagramming.deck import DeckOption, render_deck_plan, render_deck_section


def _numeric_svg(svg_text: str) -> str:
    """Fill in numeric width/height based on the viewBox for rasterisation."""
    if 'width="100%"' not in svg_text and 'height="auto"' not in svg_text:
        return svg_text
    marker = 'viewBox="'
    if marker not in svg_text:
        return svg_text
    view_box_str = svg_text.split(marker, 1)[1].split('"', 1)[0]
    parts = view_box_str.strip().split()
    if len(parts) != 4:
        return svg_text
    try:
        _, _, view_w, view_h = [float(p) for p in parts]
    except ValueError:
        return svg_text
    svg_text = svg_text.replace('width="100%"', f'width="{view_w}"', 1)
    svg_text = svg_text.replace('height="auto"', f'height="{view_h}"', 1)
    return svg_text


def load_yaml(path: Path) -> Dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, Mapping):
        raise ValueError(f"{path}: expected mapping at root")
    return dict(data)


def coerce_options(data: Mapping) -> Iterable[tuple[str, Mapping]]:
    options = data.get("options")
    if options is None:
        raise ValueError("Spec file must define an 'options' mapping")
    if isinstance(options, Mapping):
        for key, value in options.items():
            if not isinstance(value, Mapping):
                raise ValueError(f"Option {key} must be a mapping")
            yield str(key), value
    elif isinstance(options, list):
        for item in options:
            if not isinstance(item, Mapping):
                raise ValueError("Each option entry must be a mapping")
            key = item.get("key")
            if not key:
                raise ValueError("Each option entry needs a 'key'")
            yield str(key), item
    else:
        raise ValueError("'options' must be a mapping or list")


def build_deck_diagrams(
    spec_path: Path,
    data: Mapping,
    outdir: Path,
    *,
    raster: bool = False,
    png_scale: float = 2.0,
    cairosvg_mod: Optional[object] = None,
) -> None:
    scale = float(data.get("scale_px_per_meter", 100.0))
    for key, cfg in coerce_options(data):
        option = DeckOption.from_dict(key, cfg)
        plan = render_deck_plan(option, scale=scale)
        section = render_deck_section(option, scale=scale)

        option_dir = outdir / option.key.lower()
        option_dir.mkdir(parents=True, exist_ok=True)

        plan_path = option_dir / "plan.svg"
        section_path = option_dir / "section.svg"
        plan_svg = plan.to_string()
        section_svg = section.to_string()
        plan_path.write_text(plan_svg, encoding="utf-8")
        section_path.write_text(section_svg, encoding="utf-8")
        print(f"[deck] {spec_path.name}: wrote {plan_path.relative_to(outdir)} and {section_path.relative_to(outdir)}")

        if raster and cairosvg_mod is not None:
            plan_bytes = _numeric_svg(plan_svg).encode("utf-8")
            section_bytes = _numeric_svg(section_svg).encode("utf-8")
            cairosvg_mod.svg2png(bytestring=plan_bytes, write_to=str(plan_path.with_suffix(".png")), scale=png_scale)
            cairosvg_mod.svg2png(bytestring=section_bytes, write_to=str(section_path.with_suffix(".png")), scale=png_scale)


def build_attachment_diagrams(
    spec_path: Path,
    data: Mapping,
    outdir: Path,
    *,
    raster: bool = False,
    png_scale: float = 2.0,
    cairosvg_mod: Optional[object] = None,
) -> None:
    for key, cfg in coerce_options(data):
        option = AttachmentOption.from_dict(key, dict(cfg))
        svg = render_attachment_diagram(option)
        option_dir = outdir / option.key.lower()
        option_dir.mkdir(parents=True, exist_ok=True)
        svg_path = option_dir / "detail.svg"
        svg_text = svg.to_string()
        svg_path.write_text(svg_text, encoding="utf-8")
        print(f"[attachments] {spec_path.name}: wrote {svg_path.relative_to(outdir)}")

        if raster and cairosvg_mod is not None:
            svg_bytes = _numeric_svg(svg_text).encode("utf-8")
            cairosvg_mod.svg2png(bytestring=svg_bytes, write_to=str(svg_path.with_suffix(".png")), scale=png_scale)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--spec",
        action="append",
        help="Specific spec file(s) to process (default: all diagrams/specs/*.yaml)",
    )
    parser.add_argument(
        "--outdir",
        default="diagrams/output",
        help="Directory to write generated SVGs into",
    )
    parser.add_argument(
        "--png",
        action="store_true",
        help="Also rasterize each SVG to PNG (requires cairosvg)",
    )
    parser.add_argument(
        "--png-scale",
        type=float,
        default=2.0,
        help="Scale factor when rasterizing PNGs (default: 2.0)",
    )
    args = parser.parse_args()

    specs: Iterable[Path]
    if args.spec:
        specs = [Path(path) for path in args.spec]
    else:
        specs = sorted(Path("diagrams/specs").glob("*.yaml"))

    outdir = Path(args.outdir)
    cairosvg_mod = None
    if args.png:
        try:
            import cairosvg  # type: ignore

            cairosvg_mod = cairosvg
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise SystemExit("--png requested but cairosvg is not installed. pip install cairosvg") from exc

    for spec_path in specs:
        if not spec_path.exists():
            print(f"Spec {spec_path} not found, skipping")
            continue
        data = load_yaml(spec_path)
        spec_type = str(data.get("type", spec_path.stem)).lower()
        spec_outdir = outdir / spec_path.stem
        spec_outdir.mkdir(parents=True, exist_ok=True)

        if spec_type in {"deck-framing", "deck"}:
            build_deck_diagrams(spec_path, data, spec_outdir, raster=args.png, png_scale=args.png_scale, cairosvg_mod=cairosvg_mod)
        elif spec_type in {"edge-attachments", "attachments"}:
            build_attachment_diagrams(spec_path, data, spec_outdir, raster=args.png, png_scale=args.png_scale, cairosvg_mod=cairosvg_mod)
        else:
            raise ValueError(f"{spec_path}: unknown diagram type '{spec_type}'")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
