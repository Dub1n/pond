# Option C calc pack – completion checklist

Use this as a step-by-step to turn the templates into an issue-ready pack. Tick each atomic task as you go.

## 1) Set project info

- [x] Enter project/site/client, project number, calc ID/revision/date, preparer/checker/approver in calc-pack-template.md front cover.
- [x] Set reliability class, design working life, and imposed load category confirmation in Design summary.

## 2) Confirm geometry and materials

- [ ] Re-read design-C.md and option-c-dimensions.md; note any deviations agreed on site.
- [ ] Decide framing species: confirm C24 47×150 UC4 incised (or record alternative) and document in timber-options.md context.
- [ ] Decide decking species/finish (hardwood vs treated softwood vs modified softwood) and record rationale.
- [ ] Confirm hanger/strap/bracing products (manufacturer/model) for inner and outer beams.

## 3) Actions and load inputs

- [ ] Build Gk table (Section 3A): compute decking, joist, blocking, beam allowance, membranes, fixings using chosen densities; fill Result column and sources.
- [ ] Record imposed load (3.0 kN/m² balcony/terrace) with NA reference in Section 3.
- [ ] List combination factors γG/γQ/ψ and serviceability limits; ensure match Appendix-A.
- [ ] If beam self-weight kept as line load, note it in the beam worksheet.

## 4) Member checks

- [ ] Joists: compute line load w = (Gk+Qk)×0.4; analyze backspan + cantilever; get V, M at hanger; check bending, shear, deflection (instantaneous + final with kdef), vibration if needed.
- [ ] Beams: set support spacing (1.5–1.6 m or actual); apply line loads (tributary width × Gk/Qk plus beam self-weight if used); check bending, shear, deflection.
- [ ] Decking: verify 28×145 spacing at 400 mm c/c against supplier span table; note allowable span/load.
- [ ] Blocking: confirm roll restraint adequacy qualitatively or by compression check if required.

## 5) Connections and uplift

- [ ] Saddle hanger (inner beam): check required shear/bearing vs datasheet with chosen nails/screws.
- [ ] Face-mount hanger (outer beam): check shear/bearing vs datasheet with chosen fasteners.
- [ ] Top strap uplift: compute tension from cantilever peel (if considered) and check strap capacity.
- [ ] Toe-screws: check withdrawal/shear values for uplift/anti-roll per manufacturer.
- [ ] Flat-strap X-brace: size axial force from lateral restraint assumption; check strap and fixings.

## 6) Supports and bearing

- [ ] Set pad layout and spacing; compute reactions; verify against allowable bearing (Appendix-A default 200 kN/m² or site data).
- [ ] Perimeter uplift: copy `uplift-pad-check.md` outputs into the pack; confirm pad self-weight/ballast ≥ uplift (0.21 kN/pad worst-case) and note any thickening/ballast chosen.
- [ ] Note DPC/EPDM isolation and any differential settlement assumptions.

## 7) Documentation fill-ins

- [ ] Populate calc-pack-template.md: all blanks in Sections 1–7 (inputs, calculations, utilisation ratios, references).
- [ ] Update Appendix-A entries with actual manufacturer capacities and decking span verification.
- [ ] Insert checker names/dates and software/check level statements.
- [ ] Add load combination list and any model idealisations in Section 4.

## 8) QA artifacts

- [ ] Method statement: fill project details, roles, hazards, sequence tweaks if any.
- [ ] Inspection-test-plan: fill project IDs, responsible parties, hold/witness point signatories, evidence slots.
- [ ] Collate appendices: manufacturer datasheets (hangers, straps, screws), timber certificates (C24 grading, UC4), span tables, photos if available.

## 9) Final review

- [ ] Cross-check that all assumptions differing from design-C.md/timber-options.md are recorded with rationale.
- [ ] Ensure densities, loads, and factors are consistent across calc-pack, Appendix-A, and worksheets.
- [ ] Proofread for completeness; save ready for submission.
