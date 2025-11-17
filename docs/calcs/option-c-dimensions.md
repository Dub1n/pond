Option C geometry (1 m backspan, 0.25 m cantilever)
=================================================

Coordinate frame
----------------

- Deck outer frame: 5 000 mm × 5 000 mm square with top-left at (0, 0); centre at (2 500, 2 500).
- Pond aperture: 3 000 mm × 3 000 mm square centred on the deck. Edges sit at x/y = 1 000 mm and 4 000 mm.
- Walkway backspan width: (5 000 − 3 000) ÷ 2 = 1 000 mm from the pond edge to the outer rim.
- Cantilever ribbon: 250 mm inward on every side, giving an inner opening of 3 000 − 2×250 = 2 500 mm.

Plan components
---------------

- `deck_backspan`: 5 000 mm square with a concentric 3 000 mm cut-out to show the 1 000 mm walkway backspan.
- `pond_water`: 3 000 mm square aligned to the deck centre; water depth 900 mm with datum at the waterline (0 mm).
- `deck_overhang`: 3 000 mm square ring with a 2 500 mm aperture to highlight the 250 mm inward cantilever.
- `inner_beam_west`: 180 mm × (3 000 mm + 2×180 mm) beam, face-flush to the pond edge. Height 150 mm with its bottom at the water datum (0 mm) so the top aligns with joist seats at +150 mm.
- `beam_west`: 180 mm × (3 000 mm + 2×180 mm) perimeter beam. A `vertical.flush.face` keeps its bottom on the water datum as well, so both beams share the same bearing height.
- `joists_west`:
  - Joist length = backspan − beam_width + cantilever = 1 000 mm − 180 mm + 250 mm = **1 070 mm**.
  - Anchor: `pond_water` North-West aligned to joist North-East with `offset.x = cantilever` so the joist’s west face lands on the beam’s hanger line at x = 180 mm.
  - `offset.y = walkway_gap = 430 mm` keeps 430 mm clear top/bottom before the repeats step in.
  - Repeat: 6 members @ 400 mm c/c to span the 3 000 mm pond opening (3 000 − 2×430 = 2 140 mm effective run).
- `pads_west`: 300 mm × 300 mm shallow pads centred beneath each joist line.
  - Anchor to `beam_west` North edge and offset `south: walkway_gap + beam_width - (pad_size - joist_width) / 2`.
  - The expression adds the 180 mm beam setback and trims half the joist-pad width difference so the pad centre lands on the joist centreline instead of its edge.
  - `vertical.flush.face: top @ pond_water` keeps the pad tops flush with the water datum (0 mm) while the pads extend 100 mm below grade (`pad_height`).
- `soil_fill`: deck-wide fill set to the full water depth (900 mm). A `vertical.flush.face` ties its top to the water surface so the fill runs from 0 mm down to −900 mm, matching the pond excavation.
- `operations.rotate`: clones `{joists_west, pads_west, beam_west, inner_beam_west}` around the pond centre 4× so each side reuses the same layout.

Section components
------------------

- Decking: 28 mm thick, underside bears on the joist tops at +150 mm, giving a finished surface at +178 mm.
- Joists: 47×150 C24; bottoms bear on the water/soil datum (0 mm), tops at +150 mm ready for decking.
- Inner & outer beams: both 150 mm deep with their bottoms seated on the pad/soil datum (0 mm) and tops at +150 mm; the outer beam now hangs off the joist line rather than supporting it from below.
- Cantilever: 250 mm projection beyond the pond wall remains unchanged; strap/fastener requirements follow the design note.
- Pads: 300×300×100 sitting between −100 mm and 0 mm; rotated copies form the perimeter ring.
- Soil fill: 900 mm tall column from 0 mm (waterline/grade) to −900 mm.
- Water: 900 mm column from 0 mm to −900 mm; matches soil and pad datum.

Structural quick-checks
-----------------------

- Design load: 2.0 kN/m² imposed + 0.3 kN/m² finishes ⇒ 2.3 kN/m². Tributary width per joist (400 mm c/c) gives `w = 2.3 × 0.4 = 0.92 kN/m`.
- Lever arms: backspan portion is 820 mm (1 000 mm − 180 mm); cantilever remains 250 mm. Total joist length `L = 1.07 m`.
- Support reaction at the outer beam: `R = w × L = 0.92 × 1.07 ≈ 0.98 kN` per joist (before factors).
- Bending moment at the hanger line: `M = w × L² / 2 ≈ 0.92 × 1.07² / 2 ≈ 0.53 kN·m`.
  - Section modulus for a 47×150 joist: `S = b × h² / 6 = 0.047 × 0.15² / 6 ≈ 1.76×10⁻⁴ m³`.
  - Bending stress: `σ = M / S ≈ 0.53×10³ / 1.76×10⁻⁴ ≈ 3.0 MPa < 7.8 MPa (C24 allowable)`.
- Tip deflection at the 250 mm cantilever: `δ = w_c × a⁴ / (8 E I)` with `E ≈ 10 GPa`, `I = b × h³ / 12 ≈ 1.32×10⁻⁵ m⁴` → `δ ≈ 2.5 mm`.
- Pad demand: each 300×300 pad sees roughly four joists (1.6 m spacing) ⇒ `≈ 4 × 0.98 ≈ 3.9 kN` characteristic shear, easily within shallow-pad bearing capacity on compacted sub-base.
- Summary: shortening the joists to the hanger line and lifting the perimeter beam keeps both beams level, removes the torsional offset from the previous “joist-on-bearer” detail, and maintains the existing cantilever/deflection performance while the new pad alignment centres every footing under its joist line.
