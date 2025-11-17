## Target appearance for Option A plan render

The plan view should communicate which structural members sit above or below others, using architectural hidden-line conventions:

### Stack order (highest → lowest)

1. **Deck walking surface** (`deck_outer`) and **cantilever infill** (`deck_overhang`) – visible solid fill + solid outline.
2. **Joists (`joists_west` group)** – hidden beneath the decking. They must not show their solid fill anywhere the deck covers them. Instead, show their footprint only with a dashed outline that sits *above* the decking fill so the hidden framing is readable.
3. **Support beam at pond edge** (`beam_west` and rotated copies) – also hidden below the decking. Their dashed outline should appear on top of any overlapping joist outline so the hierarchy reads beam < joist < deck.
4. **Perimeter posts** (`west_posts` and rotations) – lowest elements; dashed outline should appear on top of beam/joist fills but still read as hidden (lighter stroke weight than joists, same dash pattern).
5. **Pond water opening** (`pond_water`) – this is a true void in the deck; it should remain a visible solid fill since nothing hides it.

### Linework expectations

- Hidden objects use a dashed stroke (`~18 px on / 9 px off` at export scale) in a neutral grey (#46505a) so the pattern remains visible after rasterisation.
- Hidden outlines draw *after* all fills and solid outlines so the dash is not clipped.
- Visible outlines (deck edges, pond edges) remain solid and sit on top of the dashed lines where they overlap.
- No hidden element should contribute fill colour once it is underneath another component. Their fills can render where they extend beyond the deck footprint (e.g., joists projecting past the deck perimeter).

This layout yields a deck top surface as the dominant solid shape, with dashed rectangles indicating joists, beams, and posts underneath, and the pond opening drawn as a solid void. When the PNG is generated, the dashed lines should remain clearly segmented and not appear solid due to stroke scaling.***
