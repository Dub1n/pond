# option C – joist depth check (load-driven)

> **Superseded geometry:** the calculations below use seven joists and a 250 mm projection. The as-built Design C has eight joists, a 350 mm projection, a maximum spacing of approximately 420 mm, and a 1 303 mm total straight-joist length. Do not use the results below for construction approval until they are recalculated and independently checked.

Inputs pulled from `design-C.md` and `0-Appendix-A-key-design-factors-&-material-data.md`:

- Actions: Gk = 0.457 kN/m², Qk = 3.0 kN/m²; γG = 1.35; γQ = 1.50.
- Material: C24, SC3 → fm,k = 24 N/mm², fv,k = 2.5 N/mm², kmod (imposed, SC3) = 0.70, γM = 1.30, E0,mean = 11 000 N/mm².
- Historical geometry used below: joist spacing ≈0.409 m (7 joists across 2.453 m), tributary width per joist = 0.409 m, and a 0.953 m span with a 0.25 m projection (1.203 m total). Current geometry is recorded in option-c-dimensions.md.
- Corner infill spacing: ties set at 500 mm, diagonal split at 0.707 m + 1.061 m; first/last metre of C4B sits in this corner field.

All numbers below were produced with Python shell commands so nothing is hand-waved.

## Derived actions (per metre of member)

| Case            | Formula                    | Result     |
| --------------- | -------------------------- | ---------- |
| fmd             | fm,k × kmod ÷ γM           | 12.9 N/mm² |
| fvd             | fv,k × kmod ÷ γM           | 1.35 N/mm² |
| w<sub>SLS</sub> | (Gk + Qk) × 0.409          | 1.414 kN/m |
| w<sub>ULS</sub> | (1.35·Gk + 1.5·Qk) × 0.409 | 2.093 kN/m |

## Member checks (separated at each intersection as requested)

### Historical walkway-joist calculation (outer beam to inner beam + 250 mm projection)

- Span model: simple span 0.953 m with 0.25 m overhang past the pond-edge support.
- ULS results: R<sub>outer</sub> = 0.93 kN, R<sub>pond</sub> = 1.59 kN; M<sub>max</sub> = 0.206 kN·m (positive), M<sub>pond</sub> = –0.065 kN·m (hogging at the hanger).
- SLS deflection at tip under w<sub>SLS</sub>: 47×75 → 1.40 mm; 47×100 → 0.59 mm; L/250 limit over 1.203 m = 4.8 mm.
- Bending/shear utilisation (ULS):
  - 47×75: σ = 4.68 N/mm² (0.36·fmd); τ = 0.68 N/mm² (0.50·fvd).
  - 47×100: σ = 2.63 N/mm² (0.20·fmd); τ = 0.51 N/mm² (0.38·fvd).
  - Required depth for bending alone ≈45 mm; serviceability and hanger fit push a practical minimum of 47×100 while keeping the rest at 47×150 if you want uniform tops.

### Corner ties (0.5 m span, 0.5 m tributary)

- w<sub>ULS</sub> = 2.558 kN/m; M = 0.080 kN·m; V = 0.64 kN.
- 47×75: σ = 1.81 N/mm² (0.14·fmd); τ = 0.27 N/mm² (0.20·fvd); deflection 0.08 mm (limit 2.0 mm).
- Required depth ≈28 mm → 47×75 more than covers it.

### Corner diagonal segments (0.707 m + 1.061 m, 0.5 m tributary)

- Short leg (0.707 m): M = 0.160 kN·m; 47×75 → σ utilisation 0.28; deflection 0.31 mm.
- Long leg (1.061 m): M = 0.360 kN·m; 47×75 → σ utilisation 0.63; deflection 1.57 mm (limit 4.2 mm). Required depth ≈60 mm.

### First / last metre of C4B in the corners (allowed to reduce)

- Modelled as a 1.0 m simple span with 0.5 m tributary (matching the corner tie grid).
- w<sub>ULS</sub> = 2.558 kN/m; M = 0.320 kN·m; required depth ≈56 mm.
- 47×75: σ utilisation 0.56; deflection 1.24 mm (limit 4.0 mm).

## What can shrink (and what stays at 150 mm)

- Keep 47×150 for joists running continuously along the pond edge and perimeter (C4 and the central 3 m of each C4B) for stiffness, hanger embedment, and uplift strap detailing.
- Walkway joists between the beams can be reduced to 47×100 while still sitting below 40% utilisation in bending/shear and deflection < 0.6 mm; 47×75 also passes structurally but expect hanger/strap availability and top-of-joist flushness to drive you back to 47×100 minimum.
- Corner ties, diagonal segments, and the first/last metre of each C4B can drop to 47×75 without breaching ULS or SLS limits; keep packers or consistent ledgering if you need the decking to stay flush with adjacent 150 mm members.
- If a single depth is preferred for simplicity, 47×150 everywhere is conservative; otherwise, 150 mm on the pond/perimeter runs plus 100 mm on the walk joists and 75 mm on the corner pieces satisfies the load cases above.
