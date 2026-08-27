# Perimeter uplift / pad ballast check – Option C

> **Superseded geometry:** this check uses seven joists and a 250 mm projection. Design C now has eight joists and a 350 mm projection. The results and pad-ballast conclusion below must be recalculated before they are relied upon.

Scope of the historical calculation: uplift at the outer beam (C4) pads from the former 250 mm projection over the pond edge, and resulting bending in C4 at midspan.

## Inputs and assumptions

- Geometry: backspan between outer (C4) and inner beam ≈ 0.953 m; cantilever past inner beam = 0.25 m; joist spacing ≈ 0.409 m; seven joists along the pond edge run (≈2.5 m clear between cantilevered corners). Pads along the edge at 0, 1.67, 3.33, and 5.00 m; the two interior pads take the pond-edge joist reactions.
- Loads: Gk = 0.457 kN/m² (Appendix A); Qk = 3.0 kN/m². Line loads per joist tributary: wG = 0.187 kN/m; wQ = 1.227 kN/m.
- Uplift case: leading variable load only on the cantilever, no variable load on the backspan. Stabilising self-weight taken at 0.9·Gk (as permitted for uplift), destabilising Q at 1.5·Qk.
- Pad: 300 × 300 × 100 mm concrete, density 24 kN/m³ ⇒ self-weight 0.216 kN. Adjacent sides sit almost at grade; their pads bear against the ground at the corners, so real uplift will be lower than the 1D joist-line model used here.

Computation command (run in repo root):

```bash
python - <<'PY'
from math import sqrt
L = 0.953
cantilever = 0.25
span_between_pads = 1.66
joist_spacing = 0.409
joists_per_edge = 7
E = 11_000
S = 1.76e-4
Gk_area = 0.457
Qk_area = 3.0
wG = Gk_area * joist_spacing
wQ = Qk_area * joist_spacing
factor_G_stab = 0.9
factor_Q = 1.5
def reactions_full_uniform(w_line):
    total = w_line * (L + cantilever)
    x = (L + cantilever) / 2
    Rb = total * x / L
    Ra = total - Rb
    return Ra, Rb
def reactions_cantilever_only(w_line):
    total = w_line * cantilever
    x = L + cantilever / 2
    Rb = total * x / L
    Ra = total - Rb
    return Ra, Rb
Ra_Q_only, _ = reactions_cantilever_only(wQ * factor_Q)
total_uplift = -Ra_Q_only * joists_per_edge
Ra_G_stab, _ = reactions_full_uniform(wG * factor_G_stab)
Ra_case2 = Ra_G_stab + Ra_Q_only
uplift_per_pad = total_uplift / 2
q_uplift = total_uplift / span_between_pads
M_mid = q_uplift * span_between_pads**2 / 8
M_Nmm = M_mid * 1e6
S_mm3 = S * 1e9
stress = M_Nmm / S_mm3
strain = stress / E
pad_weight = 0.3 * 0.3 * 0.1 * 24
print(f\"Line loads: wG={wG:.3f} kN/m, wQ={wQ:.3f} kN/m\")
print(f\"Ra (Q on cantilever only) = {Ra_Q_only:.4f} kN (negative = uplift)\")
print(f\"Total uplift for {joists_per_edge} joists = {total_uplift:.3f} kN\")
print(f\"Stabilised Ra with 0.9G + Q = {Ra_case2:.4f} kN (downward positive)\")
print(f\"Uplift per intermediate pad = {uplift_per_pad:.3f} kN; pad self-weight = {pad_weight:.3f} kN\")
print(f\"Self-weight margin = {pad_weight - uplift_per_pad:.3f} kN (excludes beam/joist weight)\")
print(f\"C4 span uplift line load = {q_uplift:.3f} kN/m; Mmid = {M_mid:.4f} kN·m; stress = {stress:.3f} MPa; microstrain = {strain*1e6:.1f} µε\")
PY
```

Key outputs from the command:

- Ra (Q on cantilever only) = −0.060 kN per joist ⇒ **0.422 kN total uplift** along the edge.
- Adding 0.9·Gk everywhere gives Ra = +0.014 kN (downward) per joist ⇒ **net 0.10 kN downward**, so uplift disappears once self-weight is included.
- **Uplift per interior pad = 0.211 kN** (shares the 0.422 kN between the two interior pads). Pad self-weight = 0.216 kN ⇒ **0.005 kN margin before counting beam/joist/deck weight**. A 150 mm pad would weigh ≈0.324 kN, giving a 0.113 kN margin.
- **C4 midspan under uplift:** q = 0.254 kN/m over the 1.66 m span ⇒ Mmid = 0.088 kN·m ⇒ bending stress ≈ 0.50 MPa; microstrain ≈ 45 µε. This is << C24 design stress even before kmod/γM.

## Requirements / notes

- Record in the calc pack that pad ballast must be ≥0.22 kN downward per interior pad against the 0.21 kN uplift; the existing 300 × 300 × 100 pad suffices once self-weight is counted, but thickening to 150 mm or adding local ballast gives a clear margin.
- Adjacent sides sitting on grade at the corners provide extra compression restraint; include a note that corner pads must stay in firm bearing to keep the 1D uplift case conservative.
- Reference this uplift check in the beam/pad worksheet and the connections/uplift section of calc-pack-template.md; include the command output in the issued pack.
