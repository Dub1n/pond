import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliIntegrationTests(unittest.TestCase):
    def test_build_diagrams_cli(self) -> None:
        root = Path(__file__).resolve().parents[2]
        spec_path = root / "diagramming" / "tests" / "fixtures" / "relationship_minimal.yaml"

        with tempfile.TemporaryDirectory() as tmpdir:
            outdir = Path(tmpdir) / "output"
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/build_diagrams.py",
                    "--spec",
                    str(spec_path),
                    "--collision-mode",
                    "warn",
                    "--collision-ignore",
                    "IfcFooting",
                    "--fail-on-warn",
                    "--outdir",
                    str(outdir),
                    "--force",
                ],
                check=True,
                cwd=root,
                capture_output=True,
                text=True,
            )

            self.assertIn("Building relationship-first spec", result.stdout)
            self.assertTrue((outdir / "relationship_minimal" / "x" / "plan.svg").exists())
            self.assertTrue((outdir / "relationship_minimal" / "x" / "section.svg").exists())

            png_available = importlib.util.find_spec("cairosvg") is not None
            png_path = outdir / "relationship_minimal" / "x" / "plan.png"
            if png_available and png_path.exists():
                self.assertTrue(png_path.exists())
            else:
                self.assertIn("WARNING: PNG export", result.stderr)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
