from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "docs" / "calcs" / "decking_recalcs.py"
SPEC = importlib.util.spec_from_file_location("decking_recalcs", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
decking_recalcs = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = decking_recalcs
SPEC.loader.exec_module(decking_recalcs)


class DeckingRecalcsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sources = decking_recalcs.read_sources(
            ROOT / "docs" / "calcs" / "decking-lengths.txt"
        )
        self.targets = decking_recalcs.make_targets()
        self.assignments = decking_recalcs.make_assignments(self.sources)

    def test_default_inventory_has_complete_minimum_joint_plan(self) -> None:
        decking_recalcs.validate_plan(self.assignments)
        self.assertEqual(len(self.sources), 71)
        self.assertEqual(len(self.targets), 67)
        self.assertEqual(
            sum(target.end_form == "two mitres" for target in self.targets), 5
        )

    def test_both_stock_boards_have_single_outputs(self) -> None:
        stock_assignments = [
            assignment
            for assignment in self.assignments
            if assignment.source.source_id.startswith("stock board")
        ]
        self.assertEqual(len(stock_assignments), 2)
        self.assertEqual(
            sorted(assignment.target.target_mm for assignment in stock_assignments),
            [3730, 3800],
        )

    def test_every_segment_total_and_joint_is_valid(self) -> None:
        layouts = decking_recalcs.target_layouts()
        self.assertEqual(len(layouts), 36)
        for (outside_mm, _), pieces in layouts.items():
            self.assertEqual(
                decking_recalcs._half_mm(sum(pieces)),
                decking_recalcs._half_mm(outside_mm),
            )
            inset_mm = (decking_recalcs.DECK_SPAN_MM - outside_mm) / 2
            cumulative_mm = 0.0
            for piece_mm in pieces[:-1]:
                cumulative_mm += piece_mm
                global_joint_mm = inset_mm + cumulative_mm
                centre_error_mm = min(
                    abs(global_joint_mm - centre_mm)
                    for centre_mm in decking_recalcs.JOIST_CENTRES_MM
                )
                self.assertLessEqual(
                    centre_error_mm,
                    decking_recalcs.CUT_INCREMENT_MM / 2,
                )

    def test_documented_results_match_generated_mapping(self) -> None:
        def result_rows(text: str) -> set[tuple[str, ...]]:
            rows = set()
            for line in text.splitlines():
                if not line.startswith("|"):
                    continue
                cells = tuple(cell.strip() for cell in line.strip("|").split("|"))
                if cells[0][0:1].isdigit() or cells[0].startswith("stock board"):
                    rows.add(cells)
            return rows

        generated = decking_recalcs.markdown_report(
            self.assignments, self.sources
        )
        documented = (
            ROOT / "docs" / "calcs" / "decking-recalcs.md"
        ).read_text().split("## Results", 1)[1]
        self.assertEqual(result_rows(documented), result_rows(generated))


if __name__ == "__main__":
    unittest.main()
