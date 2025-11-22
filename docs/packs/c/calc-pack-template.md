# Structural calculation package — Option C (template)

Use this template to produce the audit-ready calc pack the reviewers expect. Keep the option-C specifics below; only fill the placeholders with project/job details and calculation results. Do not change dimensions or member specs unless the design is updated in design-C.md.

---

## Front cover

- Project / Site / Client: New Inn Farm Pond
- Document title: **Structural calculation package – Pond deck (Option C)**
- Project number: 1
- Calc package ID / Revision / Date: 2025-11-18
- Prepared by / Checked by / Approved by: Gabriel Dubin
- References: design-C.md; option-c-dimensions.md; timber-options.md; manufacturer datasheets.

---

## 1. Design summary (per IStructE submission guidance)

- **Codes and NA**: EN 1990 (UK NA), EN 1991-1-1 (UK NA Table 6.2), EN 1995-1-1 (UK NA).
- **Reliability / combinations**: ULS/SLS per EN 1990 Annex A1; record chosen reliability class; design working life.
- **Stability / load path**: Deck diaphragm + blocking for joist roll; outer beam X-strap for lateral restraint; inner beam hangers carry shear; uplift resisted by top straps + opposed toe-screws.
- **Software / checking**: List any software used; describe verification/hand checks; state check level (self-check / independent simple check / third-party).
- **Responsibility**: Name responsible engineer/party for overall stability and any external review.

> Tailor: insert checker names/dates; set reliability class and imposed load category once confirmed.

---

## 2. Inputs and assumptions

- **Geometry**: 5 000 × 5 000 mm deck with 3 000 × 3 000 mm pond opening; 1 000 mm backspan; 250 mm inward cantilever each side; finished deck ≈100 mm above max water level.
- **Members**: Joists and beams 47 × 150 mm C24 UC4 incised; joists @ 400 mm c/c; solid blocking at both beam lines; decking 28 × 145 mm with 5–6 mm gaps and 20–30 mm overhang.
- **Details**: Inner beam uses top-flange saddle hangers rebated flush + top strap + opposed toe-screws; outer beam uses face-mount hangers; galvanised flat-strap X-brace at outer edge; pads 300 × 300 × 100 mm on gravel with DPC/EPDM isolation.
- **Service class / durability**: Service Class 3; preservative UC4 throughout framing; stainless A2/A4 or class 4 fasteners; reseal cut ends.
- **Environmental**: External exposure adjacent to pond; drainage slope 1–2% away from pond; liner clamp/fixings above waterline.
- **Assumption placeholders**: Insert any project-specific soil bearing assumption, snow/wind relevance (if considered), and any deviation from UC4.

> If any assumption differs from design-C.md or timber-options.md, record the change and rationale here.

---

## 3. Actions and combinations

- **Permanent (Gk)**: Self-weight of 47 × 150 framing, 28 × 145 decking, fixings; include membranes/linings if required. Insert calculated Gk.
- **Variable (Qk)**: Use balcony/terrace category with **3.0 kN/m² characteristic imposed load** to build in robustness. Record NA reference. Note: “Although primarily for private domestic use, the external nature, adjacency to water and open walk-around justify the use of balcony load category for added safety.”
- **Combination factors**: γG = 1.35; γQ = 1.50; ψ0 = 0.70; ψ1 = 0.50; ψ2 = 0.30 (balcony/external category, UK NA).
- **Serviceability limits**: Adopt L/250 for walking surface deflection; state any project-specific limits if tighter.
- **Combinations**: List ULS and SLS (characteristic/frequent/quasi-permanent) factors used, citing EN 1990 Annex A1. Insert ψ values and γF used.

> When filling, show the rationale for the chosen Qk category and any additional finishes allowance.

---

## 3A. Gk build-up (calculate before member worksheets)

Use this table to build Gk (kN/m²) from densities. Enter sources (supplier/EN 1991-1-1 Annex A). For beam checks you may keep beam self-weight as a line load instead of folding it into area Gk.

| Component                             | Assumed density (kN/m³) | Calculation (show working)                                                                   | Result (kN/m²) | Source (datasheet/EC)          |
| ------------------------------------- | ----------------------- | -------------------------------------------------------------------------------------------- | -------------- | ------------------------------ |
| Decking 28 × 145                      | 9.5 [2]                 | Boards per m = 1/(0.145+0.006)=6.62; volume =0.028×0.145×6.62=0.02689 m³/m² → ×9.5           | 0.255          | Hardwood range (Balau/Ipe) [2] |
| Joists 47 × 150 @ 400 c/c             | 5.3 [1]                 | (0.047 × 0.150 / 0.40) × 5.3                                                                 | 0.093          | Softwood + UC4 allowance [1]   |
| Blocking allowance (47 × 150)         | 5.3 [1]                 | Two 0.4 m blocks per joist: 0.047×0.150×0.40×2=0.00564 m³; ×5.3/1.07=0.0279 kN/m line; /0.40 | 0.070          | Softwood + UC4 allowance [1]   |
| Beam allowance (47 × 150)             | 5.3 [1]                 | Kept as line load for beam design: 0.047×0.150×5.3 = 0.037 kN/m (excluded from area sum)     | —              | Softwood + UC4 allowance [1]   |
| Membrane / finishes                   | 11.0 [3]                | 3 mm EPDM/DPC allowance: 0.003 × 11.0                                                        | 0.033          | EPDM/DPC density approx. [3]   |
| Fixings / misc.                       | 78.5 [4]                | Allow 0.5 kg/m² stainless screws/strap = 0.005 kN/m²                                         | 0.005          | Stainless steel density [4]    |
| **Total Gk (use in w = (Gk+Qk)×0.4)** | —                       | Sum above                                                                                    | **0.457**      | —                              |

> If expressing beam self-weight as a line load, note it separately in the beam worksheet and exclude it from the area Gk used for joist line load.

---

## 4. Global model and idealisations

- Joists span between outer and inner beams, simply supported with 250 mm cantilever past the inner beam.
- Beams continuous, tops flush with joists; bearing height aligned with pad datum (0 mm) per option-c-dimensions.md.
- Tributary width per joist: 0.4 m (400 mm c/c).
- Support spacing for beams: 1.5–1.6 m centres on 300 × 300 pads (confirm actual spacing used).
- Bracing: Deck diaphragm + blocking; outer beam X-strap fixed every other hole, tensioned.
- Idealisation placeholders: Note any model simplifications (e.g., neglecting diaphragm stiffness, end fixity) and justify.

---

## 5. Member checks (EN 1995-1-1)

Use the worksheet in Section 7 for each member type. Keep the provided sizes; insert calculation outputs and utilisation ratios.

- **Joists 47 × 150**: bending, shear, bearing at hangers, cantilever tip deflection SLS, vibration if required.
- **Beams 47 × 150**: bending, shear, deflection; support reactions matched to pad layout.
- **Deck boards 28 × 145**: span vs 400 mm c/c; check against supplier table.
- **Blocking**: compression/roll restraint adequacy (qualitative unless calculated).

---

## 6. Connections and stability checks

- **Inner beam**: Saddle hanger shear/bearing per manufacturer; top strap tension; opposed toe-screw withdrawal/shear for uplift; blocking tight for roll restraint.
- **Outer beam**: Face-mount hanger shear/bearing; optional toe-screws to remove play.
- **Bracing**: Flat-strap X-brace axial capacity and fixings; confirm strap grade and screw/nail type.
- **Uplift/peel**: State calculation of uplift forces if applicable; otherwise record “not governing” with justification.
- **Corrosion**: Confirm stainless/class 4 fasteners and compatibility with hangers/straps.

Placeholders: insert manufacturer references, fastener schedules, and utilisation ratios once known.

---

## 7. Worksheet template (fill per member/connection)

Use this for joists, beams, hangers, straps. Prefill the option-C geometry and tributary data; complete the blanks with calculated values.

```calc
WORKED EXAMPLE – OPTION C (fill blanks)

1. MEMBER
   Joist – 47×150 C24 UC4
   Span: backspan 1 000 mm – beam width 180 mm = 820 mm; cantilever 250 mm; total length 1.07 m. [Ref: option-c-dimensions.md]
   Spacing: 400 mm c/c; tributary width = 0.4 m.

2. INPUT DATA
   Gk (self-weight + finishes) = 0.457 kN/m²
   Qk (imposed) = 3.0 kN/m² [Balcony/terrace category per EN 1991-1-1 Table 6.2; rationale: external, adjacent to water, open walk-around]
   Material: C24; Service class: 3; Treatment: UC4 incised; kmod/kdef/γM per EN 1995-1-1 (UK NA).

3. TO FIND
   Example: Check joist (47×150) with 250 mm cantilever for bending, shear, deflection (ULS/SLS).

4. ACTIONS
   Permanent (Gk): 0.457 kN/m² (from Table 3A)
   Variable (Qk): balcony/terrace = 3.0 kN/m² (EN 1991-1-1 Table 6.2)
   Load combinations (EN 1990 A1): ULS = γG·Gk + γQ·Qk = 1.35·Gk + 1.50·Qk; SLS (char/freq/quasi-perm) = Gk + Qk; Gk + ψ1·Qk; Gk + ψ2·Qk.

5. ANALYSIS
   Line load w = (Gk + Qk) × 0.4 = (0.457+3.0)×0.4 = 1.383 kN/m
   Backspan Lb = 0.82 m; cantilever a = 0.25 m; total joist length L = 1.07 m
   Reactions/internal forces at hanger line: V = ___; M = ___  [add free-body sketch reference]

6. DESIGN CHECKS (EN 1995-1-1)
   Service class = 3; load duration = medium-term for imposed load; kmod = 0.70 (medium-term SC3) or 0.90 (short-term SC3) per action; kdef = 2.0; γM = 1.3
   Section props 47×150: b = 0.047 m; h = 0.150 m; I = 1.32×10^-5 m^4; S = 1.76×10^-4 m^3
   Bending: σm,Ed = M / S ≤ fm,d → OK/NG
   Shear:  τEd = V / (b×h) × 0.67 ≤ fv,d → OK/NG
   Deflection SLS: δinst, δfin ≤ limits (cite NA limits) → OK/NG
   Vibration (if required): comment / calc / N/A

7. CONNECTIONS
   Hanger: required shear/bearing vs manufacturer capacity → OK/NG
   Uplift restraint (strap + toe-screws): design tension/withdrawal → OK/NG
   Bracing (outer beam X-strap where relevant): axial forces & fixings → OK/NG

8. SUPPORTS
   Pad reaction at spacing = ____ m → bearing check on sub-base → OK/NG

9. RESULT / CONCLUSION
   Member/connection passes with utilisation ratios: Bending __%, Shear __%, Deflection __%.

10. CROSS-REFS
    Sketch/Detail: DWG ___; Manufacturer sheet ___; Appendix page ___.

CHECKED BY: ___________   SIGN: ______   DATE: __/__/__
```

> Keep the given dimensions and section properties; only fill the blanks with calculated forces, kmod factors, and utilisation ratios.

---

## 8. Attachments and appendices

- GA/section sketches showing hanger rebates, X-brace route, liner clamp location.
- Manufacturer datasheets and fastener schedules for saddle hangers, face-mount hangers, straps, screws.
- Timber certificates: C24 grading; UC4 incised treatment.
- Photos for ITP hold/witness points (pads, hangers, straps, bracing, liner clamp, decking fall/gaps).
- Risk assessment (RAMS) and signed Method Statement.

> Before issue, list each appendix item with filename/reference and confirm inclusion.

---

References  
[1] https://eurocodeapplied.com/design/en1991/annex-A  
[2] https://www.wood-database.com/yellow-balau/  
[3] https://www.engineeringtoolbox.com/rubber-epdm-d_2042.html  
[4] https://www.engineeringtoolbox.com/metal-alloys-densities-d_50.html
