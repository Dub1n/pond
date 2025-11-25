#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List, Optional

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from diagramming import DiagramPlanner
from diagramming.relationships import is_relationship_schema, relationship_mode_enabled
from diagramming.renderers import SvgRenderer

try:  # optional dependency (pyrender + pyglet)
    from diagramming.renderers import render_orthographic_png
except ImportError:  # pragma: no cover - optional dependency path
    render_orthographic_png = None  # type: ignore[misc]
from diagramming.schema import DiagramSpec, load_spec
from diagramming.planner.exporters import GltfExporter, GltfExportOptions


SVG_DASH_SCALE = SvgRenderer.DEFAULT_DASH_SCALE
PNG_DASH_SCALE = 1.0


def find_spec_paths(explicit: Iterable[str]) -> List[Path]:
    if explicit:
        return [Path(spec) for spec in explicit]
    default_dir = Path("diagrams/specs")
    if not default_dir.exists():
        raise SystemExit(
            "No specs provided and default directory 'diagrams/specs' not found"
        )
    return sorted(default_dir.glob("*.yaml"))


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build pond deck diagrams from declarative specs."
    )
    parser.add_argument(
        "--spec",
        action="append",
        help="Path to a spec YAML file. Defaults to all specs in diagrams/specs/ if not provided.",
    )
    parser.add_argument(
        "--option",
        action="append",
        dest="options",
        help="Limit rendering to specific option keys (case-sensitive).",
    )
    parser.add_argument(
        "--outdir",
        default="diagrams/output",
        help="Directory to write generated diagrams into (default: diagrams/output).",
    )
    parser.add_argument(
        "--no-png",
        action="store_true",
        help="Skip PNG snapshots (SVGs are always written).",
    )
    parser.add_argument(
        "--no-gltf",
        action="store_true",
        help="Skip glTF exports (model.glb).",
    )
    parser.add_argument(
        "--gltf-format",
        choices=("glb", "gltf"),
        default="glb",
        help="glTF output format (default: glb).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing output files.",
    )
    parser.add_argument(
        "--orthographic",
        action="store_true",
        help="Render an orthographic PNG (requires pyrender + pyglet).",
    )
    parser.add_argument(
        "--orthographic-size",
        type=int,
        default=1024,
        help="Output size (pixels) for the orthographic PNG (default: 1024).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    spec_paths = find_spec_paths(args.spec or [])
    if not spec_paths:
        print("No spec files found.", file=sys.stderr)
        return 1

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    png_requested = not args.no_png
    cairosvg = None
    if png_requested:
        try:
            import cairosvg as _cairosvg  # type: ignore[import-not-found]
        except ImportError:
            print(
                "WARNING: PNG export requested but cairosvg is unavailable. "
                "Install cairosvg to enable PNG outputs.",
                file=sys.stderr,
            )
            png_requested = False
        else:
            cairosvg = _cairosvg

    for spec_path in spec_paths:
        raw = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and is_relationship_schema(raw.get("schema")):
            flag_notice = (
                " Set POND_RELATIONSHIPS=1 once the solver is ready."
                if not relationship_mode_enabled()
                else ""
            )
            print(
                f"Spec {spec_path} is marked as relationship-first; "
                "build_diagrams currently supports legacy specs only. "
                "Run scripts/lint_specs.py for validation while the solver is landing."
                f"{flag_notice}",
                file=sys.stderr,
            )
            return 1
        spec = load_spec(spec_path, include_options=args.options)
        planner = DiagramPlanner(spec)
        renderer = SvgRenderer()
        gltf_requested = not args.no_gltf
        gltf_options = GltfExportOptions(file_format=args.gltf_format)
        gltf_exporter = GltfExporter(gltf_options) if gltf_requested else None

        print(f"Building spec {spec.name} from {spec_path}")
        for option_key in spec.option_keys():
            if args.options and option_key not in args.options:
                continue
            planned_views = []
            option = spec.get_option(option_key)
            plan_bundle = None
            for view_name in option.view_names():
                planned = planner.plan(option_key, view_name)
                planned_views.append(planned)
                if planned.view == "plan":
                    plan_bundle = planned.bundle

            for planned in planned_views:
                output_dir = outdir / spec.name / planned.option.key.lower()
                output_dir.mkdir(parents=True, exist_ok=True)
                svg_path = output_dir / f"{planned.view}.svg"
                png_path = output_dir / f"{planned.view}.png"

                if svg_path.exists() and not args.force:
                    print(f"  Skipping existing {svg_path} (use --force to overwrite)")
                    continue

                aria_label = (
                    planned.view_config.aria_label if planned.view_config else None
                )
                title = planned.view_config.title if planned.view_config else None
                svg_data = renderer.render(
                    planned.bundle,
                    aria_label=aria_label,
                    title=title,
                    dash_scale=SVG_DASH_SCALE,
                )
                svg_path.write_text(svg_data, encoding="utf-8")
                print(f"  Wrote {svg_path.relative_to(outdir)}")

                if png_requested and cairosvg is not None:
                    png_svg_data = svg_data
                    if PNG_DASH_SCALE != SVG_DASH_SCALE:
                        png_svg_data = renderer.render(
                            planned.bundle,
                            aria_label=aria_label,
                            title=title,
                            dash_scale=PNG_DASH_SCALE,
                        )
                    cairosvg.svg2png(
                        bytestring=png_svg_data.encode("utf-8"), write_to=str(png_path)
                    )
                    print(f"  Wrote {png_path.relative_to(outdir)}")

            if gltf_exporter and plan_bundle:
                gltf_filename = f"model.{args.gltf_format}"
                gltf_path = outdir / spec.name / option_key.lower() / gltf_filename
                gltf_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    gltf_exporter.export(plan_bundle, gltf_path)
                except ValueError as exc:
                    print(f"  Skipped glTF export: {exc}")
                else:
                    print(f"  Wrote {(gltf_path.relative_to(outdir))}")

            if args.orthographic:
                if render_orthographic_png is None:
                    print(
                        "  Skipped orthographic render: pyrender/pyglet not available.",
                    )
                elif plan_bundle is None:
                    print("  Skipped orthographic render: plan view not generated.")
                else:
                    ortho_path = (
                        outdir / spec.name / option_key.lower() / "orthographic.png"
                    )
                    if ortho_path.exists() and not args.force:
                        print(
                            f"  Skipping existing {ortho_path.relative_to(outdir)} (use --force to overwrite)"
                        )
                    else:
                        try:
                            render_orthographic_png(
                                plan_bundle,
                                ortho_path,
                                image_size=args.orthographic_size,
                            )
                        except Exception as exc:  # pragma: no cover - safeguard
                            print(f"  Skipped orthographic render: {exc}")
                        else:
                            print(f"  Wrote {ortho_path.relative_to(outdir)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
