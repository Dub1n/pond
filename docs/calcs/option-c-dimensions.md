Option C geometry (1 m backspan, 0.25 m cantilever)
===================================================

Coordinate frame
----------------

- Deck outer frame: 5 000 mm × 5 000 mm square with top-left at (0, 0); centre at (2 500, 2 500).
- Pond aperture: 3 000 mm × 3 000 mm square centred on the deck. Edges sit at x/y = 1 000 mm and 4 000 mm.
- Walkway backspan width: (5 000 − 3 000) ÷ 2 = 1 000 mm from the pond edge to the outer rim.
- Cantilever ribbon: 250 mm inward on every side, giving an inner opening of 3 000 − 2×250 = 2 500 mm.
- Corner reference: deck corners at (0, 0), (0, 5), (5, 0), (5, 5); overhang tips at (1.25, 1.25) etc.

Plan components
---------------

- `deck_backspan`: 5 000 mm square with a concentric 3 000 mm cut-out to show the 1 000 mm walkway backspan.
- `pond_water`: 3 000 mm square aligned to the deck centre; water depth 900 mm with datum at the waterline (0 mm).
- `deck_overhang`: 3 000 mm square ring with a 2 500 mm aperture to highlight the 250 mm inward cantilever.
- `inner_beam_west`: 47 × 150 mm beam running the full 5 000 mm depth, face-flush to the pond edge. Bottom at the water datum (0 mm) so the top aligns with joist seats at +150 mm; ends extend to the corners.
- `beam_west`: 47 × 150 mm perimeter beam, also full-depth to the corners. `vertical.flush.face` keeps its bottom on the water datum so both beams share the same bearing height.
- `joists_west`:
  - Joist length = backspan − beam_width + cantilever = 1 000 − 47 + 250 = **1 203 mm**.
  - Anchor: `pond_water` North-West aligned to joist North-East with `offset = [cantilever, cantilever]` so the first joist face is flush with the overhang edge (top of the 2.5 m aperture) **1 250 mm in from the deck perimeter**.
  - Repeat: 7 members across the 2 500 mm overhang width using `span = pond_span − 2×cantilever − joist_width = 2 453 mm`, `direction: south` ⇒ spacing ≈ 409 mm c/c; last joist south face lands flush with the opposite overhang edge, keeping the run bounded by the cantilever edges.
- `corner_diagonal`: 47×150 joist running from the deck corner to the end of the 250 mm overhang (hypotenuse ≈ 1 770 mm for a 1.25 m × 1.25 m right triangle).
- `corner_ties`: two 47×150 joists per corner tying the diagonal back to the perimeter at 500 mm from each corner along X and Y, keeping the corner field under the 550 mm spacing limit.
- `pads_west`: 300 mm × 300 mm shallow pads supporting the **outer beam**.
  - Place pads at the north-west and south-west corners plus two intermediates per edge aligned to joist lines **#2 (y ≈ 1 667 mm)** and **#6 (y ≈ 3 333 mm)** so pad centrelines coincide with joist centrelines.
  - Repeat the same four positions on each side via `operations.rotate` so the perimeter has 12 pads total; corners share pads between orthogonal beams.
- `soil_fill`: deck-wide fill set to the full water depth (900 mm). A `vertical.flush.face` ties its top to the water surface so the fill runs from 0 mm down to −900 mm, matching the pond excavation.
- `operations.rotate`: clones `{joists_west, pads_west, beam_west, inner_beam_west, corner_diagonal, corner_ties}` around the pond centre 4× so each side reuses the same layout and every corner is framed.

Section components
------------------

- Decking: 28 mm thick, underside bears on the joist tops at +150 mm, giving a finished surface at +178 mm.
- Joists: 47×150 C24; bottoms bear on the water/soil datum (0 mm), tops at +150 mm ready for decking. Corner diagonals and ties use the same size and elevation.
- Inner & outer beams: both 47×150 with their bottoms at the pad/soil datum (0 mm) and tops at +150 mm; beam extensions meet at corners.
- Cantilever: 250 mm projection beyond the pond wall remains unchanged; strap/fastener requirements follow the design note.
- Pads: 300×300×100 sitting between −100 mm and 0 mm; rotated copies form the perimeter ring.
- Soil fill: 900 mm tall column from 0 mm (waterline/grade) to −900 mm.
- Water: 900 mm column from 0 mm to −900 mm; matches soil and pad datum.

Structural quick-checks
-----------------------

- Design load: 2.0 kN/m² imposed + 0.3 kN/m² finishes ⇒ 2.3 kN/m². Tributary width per joist ≈ 0.409 m ⇒ `w ≈ 0.94 kN/m`.
- Lever arms: backspan portion is 953 mm (1 000 − 47); cantilever remains 250 mm. Total joist length `L = 1.203 m`.
- Support reaction at the outer beam: `R = w × L ≈ 0.94 × 1.203 ≈ 1.13 kN` per joist (before factors).
- Bending moment at the hanger line: `M = w × L² / 2 ≈ 0.94 × 1.203² / 2 ≈ 0.68 kN·m`.
  - Section modulus for a 47×150 joist: `S = b × h² / 6 = 0.047 × 0.15² / 6 ≈ 1.76×10⁻⁴ m³`.
  - Bending stress: `σ = M / S ≈ 0.68×10³ / 1.76×10⁻⁴ ≈ 3.9 MPa < 7.8 MPa (C24 allowable)`.
- Tip deflection at the 250 mm cantilever: `δ = w_c × a⁴ / (8 E I)` with `E ≈ 10 GPa`, `I = b × h³ / 12 ≈ 1.32×10⁻⁵ m⁴` → `δ ≈ 3 mm`.
- Pad demand: with 4 pads per edge (corner + joists #2 and #6), the longest outer-beam span ≈1.67 m. Reactions ≈2.3 kN at intermediates; a corner pad supports two beams (~4.6 kN combined). All remain within 300×300 bearing on compacted sub-base. Pond-edge support is assumed adequate and may use an alternate detail in lieu of pads.
- Corner diagonals (1.77 m effective length) sit at 45°; tributary decking is a mitered triangle held within 500 mm of a support along both legs, keeping bay widths < 550 mm.
- Summary: spanning only the 2.5 m overhang width with 7 joists (~409 mm c/c) keeps members inside the cantilever band, trims component count, and maintains capacity/deflection margins.
