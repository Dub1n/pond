#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from diagramming.relationships import (  # noqa: E402
    SchemaError,
    is_relationship_schema,
    lint_relationship_spec,
    load_relationship_spec,
    validate_relationship_spec,
)
from diagramming.schema import load_spec  # noqa: E402
from diagramming.schema.ifc_lint import lint_ifc_metadata  # noqa: E402


def find_spec_paths(explicit: Iterable[str]) -> List[Path]:
    if explicit:
        return [Path(item) for item in explicit]
    default_paths: List[Path] = []
    phase3_dir = Path("diagrams/specs")
    if phase3_dir.exists():
        default_paths.extend(sorted(phase3_dir.glob("*.yaml")))
    return default_paths


def parse_args(argv: List[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint legacy and relationship-first deck specs.")
    parser.add_argument(
        "--spec",
        action="append",
        dest="specs",
        help="Specific spec files to lint (defaults to diagrams/specs/*.yaml).",
    )
    parser.add_argument(
        "--relationship-only",
        action="store_true",
        help="Only lint relationship-first specs.",
    )
    parser.add_argument(
        "--legacy-only",
        action="store_true",
        help="Only lint legacy specs using the current planner schema.",
    )
    parser.add_argument(
        "--collision-mode",
        choices=("error", "warn", "ignore"),
        help="Override collision handling severity for relationship specs.",
    )
    parser.add_argument(
        "--collision-ignore",
        help="Comma-separated IFC classes to skip during collision checks.",
    )
    parser.add_argument(
        "--fail-on-warn",
        action="store_true",
        help="Promote solver warnings to errors (sets DIAGRAM_RELATIONSHIPS_FAIL_ON_WARN=1).",
    )
    return parser.parse_args(argv)


def lint_path(path: Path, *, relationship_only: bool, legacy_only: bool) -> Tuple[bool, List[str]]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    spec_is_relationship = is_relationship_schema(raw.get("schema") if isinstance(raw, dict) else None)

    if relationship_only and not spec_is_relationship:
        return True, []
    if legacy_only and spec_is_relationship:
        return True, []

    if spec_is_relationship:
        try:
            spec = load_relationship_spec(path)
            errors = lint_relationship_spec(spec)
            report = validate_relationship_spec(spec)
            errors.extend(report.errors)
            warnings = report.warnings
        except SchemaError as exc:
            return False, [f"{path.name}: {exc}"]
        messages: List[str] = []
        if warnings:
            messages.extend([f"{path.name}: warning: {warn}" for warn in warnings])
        if errors:
            prefixed = [f"{path.name}: {err}" for err in errors]
            prefixed.extend(messages)
            return False, prefixed
        checksum_note = f" (mesh {report.mesh_checksum[:12]})" if report.mesh_checksum else ""
        messages.append(f"{path.name}: relationship-first lint passed{checksum_note}")
        return True, messages

    try:
        spec = load_spec(path)
    except Exception as exc:  # pragma: no cover - defensive
        return False, [f"{path.name}: legacy schema failed validation ({exc})"]
    ifc_errors = lint_ifc_metadata(spec)
    if ifc_errors:
        prefixed = [f"{path.name}: {err}" for err in ifc_errors]
        return False, prefixed
    return True, [f"{path.name}: legacy lint passed"]


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)
    if args.collision_mode:
        os.environ["DIAGRAM_RELATIONSHIPS_COLLISIONS"] = args.collision_mode
    if args.collision_ignore:
        os.environ["DIAGRAM_RELATIONSHIPS_COLLISIONS_IGNORE_CLASSES"] = args.collision_ignore
    if args.fail_on_warn:
        os.environ["DIAGRAM_RELATIONSHIPS_FAIL_ON_WARN"] = "1"
    spec_paths = find_spec_paths(args.specs or [])
    if not spec_paths:
        print("No spec files found.", file=sys.stderr)
        return 1

    all_ok = True
    messages: List[str] = []
    for path in spec_paths:
        ok, details = lint_path(path, relationship_only=args.relationship_only, legacy_only=args.legacy_only)
        all_ok = all_ok and ok
        messages.extend(details)

    for line in messages:
        print(line)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
