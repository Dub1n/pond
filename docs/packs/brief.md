I read through your three deck docs and pulled the key facts I’ll reference below (5×5 m outer frame with a 3×3 m pond opening; 1 m walkway backspan; 250mm inward cantilever; C24 UC4 47×150 joists/beams at 400mm c/c; saddle hangers/straps at the pond edge; face‑mount hangers and X‑brace at the outer edge; 28×145 decking; 1–2% fall away from pond, etc.).

Below are two things your reviewers will instantly recognize:

1. an **audit‑ready structural calculation pack format** (with a fill‑in template), aligned to Eurocodes/IStructE guidance; and
2. an **industry‑standard “construction play‑by‑play”** made of a concise Method Statement + an ITP (Inspection & Test Plan) you can fill out once the calcs are final.

Where I say “should include” I’m following IStructE’s submission guidance (design summary, codes used, basis of design, stability/load path, software & checking, etc.). That’s exactly what Building Control (and peers) expect to see in a calculation package.

---

## A) Audit‑ready calculation pack — what “standard” looks like

**References to anchor your pack:**

* **IStructE: “Guidance on the submission of structural calculations to Building Control”** – calls for a **design summary** listing the codes used, basis of design, load path/stability explanation, who’s responsible for overall stability, what software was used and how it was verified, and what checking took place.
* **EN 1990 (Eurocode 0 – Basis of structural design)** – sets the overarching reliability format, load combinations, and the need to state the National Annex choices.
* **EN 1991‑1‑1 (Actions on structures)** – gives imposed load categories (e.g., **Category A domestic floors ~2.0 kN/m²**; **balconies 2.5–4.0 kN/m²**; the UK NA may set specific values). Your checker will pick between “domestic area” vs “balcony/external deck” depending on use and access. ([Eurocodes][1])
* **EN 1995‑1‑1 (Eurocode 5 – Timber)** – use for C24 softwood members, **service class** assignment (likely SC3 adjacent to water), load duration, kmod/kdef factors, and connection design rules.

> **Note on loads for decks:** Private domestic external decks are commonly designed at **2.0–3.0 kN/m²** depending on classification and client brief. Eurocode 1 Table 6.2 shows **Category A floors 1.5–2.0 kN/m²** and **balconies 2.5–4.0 kN/m²**; many UK deck guides (and some housebuilder criteria) push higher values for robustness. Choose the category deliberately and record the rationale in the Design Basis. ([Eurocodes][1])

---

### A1) Calculation pack structure (section‑by‑section)

**Front Cover**:

* Project, site, client
* Document title (“Structural calculation package – Pond deck (Option C)”)
* Project number, calc package ID, revision, date
* Prepared by / Checked by / Approved by

**1. Design Summary**: *(per IStructE submission guidance)*

* Codes & National Annexes used; e.g., **EN 1990/1991/1995 with UK NA**.
* Basis of design (ULS/SLS combinations; design working life; reliability class).
* Building/disproportionate collapse class (if relevant), stability strategy, and **load path narrative**.
* Software used (if any) with **verification note**; scope of hand checks.
* Responsibility for overall stability and the scope of any third‑party checks.

**2. Inputs & Assumptions**:

* **Geometry** (5 000×5 000mm deck with 3 000×3 000mm pond; 1 000mm backspan; 250mm inward cantilever).
* **Members & spacing** (C24 UC4 47×150 joists/beams @ 400mm c/c; 28×145 decking).
* **Details affecting analysis** (inner beam saddle hangers + straps; outer beam face‑mount hangers + X‑bracing; blocking).
* **Timber service class** (likely **SC3** given proximity to water); preservative **UC4 incised** for framing per spec.  
* **Materials** (strength class C24; connection hardware to manufacturer tables; stainless A2/A4 or class 4 fixings).
* **Environmental** (external, wetting risk at pond edge; drainage slope 1–2%).

**3. Actions & Combinations**:

* **Permanent actions (Gk)**: self‑weight of members, decking, fixings, etc.
* **Variable actions (Qk)**: pick category and value from **EN 1991‑1‑1 Table 6.2** (record NA choice).
* **ULS/SLS combinations** per **EN 1990 Annex A1** – list coefficients used (γF, ψ0, ψ1 as applicable).

**4. Global model / Simplifications**:

* Tributary widths, spans, cantilever zones; support conditions at inner/outer beams; lateral bracing by deck diaphragm and X‑strap.
* Any idealisations (e.g., joists as simply supported with cantilever; inner/outer beams as continuous with support spacing).

**5. Member checks (EN 1995‑1‑1)**:

* **Joists (47×150)**: bending, shear, bearing at hangers, **cantilever tip deflection SLS**; vibration (if required by client/spec).
* **Beams (47×150)**: bending, shear, deflection; **support reactions** vs pads spacing.
* **Deck boards**: span vs thickness and c/c spacing (28×145 at 400mm c/c).
* **Service class & duration** → kmod/kdef; **γM**; final deflections.

**6. Connections & Uplift restraint**:

* **Saddle hangers (inner beam)**: manufacturer capacity check (shear, bearing, top‑flange embed, fixings).
* **Top straps + toe‑screws**: uplift/peel verification and withdrawal/rope‑effect checks.
* **Face‑mount hangers (outer beam)**; **X‑brace** sizing/fixings and racking restraint rationale. *(Attach manufacturer datasheets to Appendix.)*

**7. Supports & Ground interface**:

* **Pad schedule** (300×300×100mm pads at ~1.5–1.6 m centres; DPC/EPDM isolation). Bearing pressures and settlement commentary.

**8. Durability & Detailing**:

* **UC4 incised pine** for framing; reseal cut ends; stainless fasteners; liner isolation; drainage slope; board gaps; drip kerf.

**9. Construction sequence / temporary conditions**:

* Note any stages where partial fixity or unbraced lengths govern (e.g., before X‑bracing and blocking are installed).

**10. Results & Compliance statement**:

* Tabular summary: pass/fail margins for each element and connection; governing clauses/capacities.

**11. Checking & Verification**:

* Named **checker**, date, signature; **check level** (self‑check vs independent review). (SER/IStructE and temporary‑works practice describe check levels from self‑check through fully independent checks.) ([ser-ltd.com][2])

**12. Appendices**:

* Sketches/GA drawings, manufacturer data sheets, span tables (if used), calculation printouts, materials certificates, and any geotechnical notes.

---

### A2) Per‑sheet calculation **worksheet** layout (copy/paste template)

> **Header (on every page)** – Project │ Calc title │ Calc ID │ **By / Chk / App** │ Date │ Rev │ Units (SI) │ Page x of y
> *(Including these fields on each sheet is standard engineering admin practice in structural design manuals.)* ([transportation.ky.gov][3])

```markdown
PROJECT:  ____________________________________     JOB No: _____________
LOCATION: ____________________________________     CALC No: _____________
TITLE:    ____________________________________     REV:  __  DATE: __/__/__
BY: ________   CHK: ________  APP: ________       UNITS: SI (N, mm, kN/m, MPa)

1. REFERENCES / CODES
   EN 1990 (UK NA), EN 1991‑1‑1 (Table 6.2 + UK NA), EN 1995‑1‑1 (UK NA),
   Manufacturer data: [hanger/strap], TDCA guidance (for good practice as relevant).
   Assumptions and Nationally Determined Parameters listed in Design Summary.

2. GIVEN (FROM SPEC / DRAWINGS)
   Geometry: outer 5.0×5.0 m; inner pond 3.0×3.0 m; backspan 1.0 m; cantilever 0.25 m.  [Ref: Spec]
   Members: C24 UC4 47×150 joists/beams @ 400 c/c; 28×145 deck boards.  [Ref: Spec]
   Details: inner beam saddle hangers+strap; outer beam face-mount hangers + X-brace; blocking.  [Ref: Spec]

3. TO FIND
   Example: Check joist (47×150) with 250 mm cantilever for bending, shear & deflection (ULS/SLS).

4. ACTIONS
   Permanent (Gk): [calc self-weight…]
   Variable (Qk): Category [A/Balcony] = [____] kN/m² (EN 1991‑1‑1 Table 6.2; UK NA note).
   Load combs (EN 1990 A1): ULS = … ; SLS (char/freq/quasi-perm) = …

5. ANALYSIS
   Tributary width = 0.4 m → line load w = (Gk + Qk) × 0.4 = ______ kN/m
   Backspan Lb = 1.0 m – beam width allowance; cantilever a = 0.25 m; total joist length L = ___ m
   Reactions / internal forces at hanger line: V = ___; M = ___  [free-body sketch]

6. DESIGN CHECKS (EN 1995‑1‑1)
   Material factors: service class = ___; load duration class = ___; kmod = ___; kdef = ___; γM = ___
   Section properties (47×150): b = 0.047 m; h = 0.150 m; I = ___; S = ___
   Bending: σm,Ed = M / S ≤ fm,d  → OK/NG
   Shear:  τEd = V / (b×h) × [0.67] ≤ fv,d  → OK/NG
   Deflection SLS: δinst, δfin ≤ limits (note NA limits)  → OK/NG
   Vibration (if required): comment / calc / N/A.

7. CONNECTIONS
   Hanger: required shear/bearing vs manufacturer capacity → OK/NG
   Uplift restraint (strap + toe-screws): design tension/withdrawal → OK/NG
   Bracing (outer beam X‑strap): axial forces & fixings → OK/NG

8. SUPPORTS
   Pad reaction at spacing = ____ m → bearing check on sub‑base → OK/NG

9. RESULT / CONCLUSION
   Member/connection passes with utilisation ratios: Bending __%, Shear __%, Deflection __%.

10. CROSS‑REFS
   Sketch/Detail: DWG ___; Manufacturer sheet ___; Appendix page ___.

CHECKED BY: ___________ SIGN: ______  DATE: __/__/__
```

> Where you pull numbers from your own spec, reference it inline (e.g., “Ref: design‑C.md §framing summary; Option‑C geometry”).

---

## B) “Construction play‑by‑play” (Method Statement + ITP)

In UK construction, the “play‑by‑play” is a **Method Statement (safe system of work)** paired with an **Inspection & Test Plan** that sets out *what* must be checked, *when*, *by whom*, and the **hold/witness points** controlling progress. HSE describes method statements as the step‑by‑step safe method, typically used alongside a risk assessment (RAMS). ([HSE][4])
ITPs are standard QA/QC instruments (ISO 9001‑aligned) listing inspections, acceptance criteria, and records. The CQI/ConSIG template is a good model. ([Consig][5])

### B1) Short Method Statement template (deck around pond)

**Document control**
Project / Location / MS No. / Rev / Date / Prepared by / Reviewed by / Approved by

**Scope & references**:

* Build low‑profile timber deck around 3×3 m pond with 1 m walk‑around and 250mm inward overhang; finishes ≈100mm above max water level.
* Drawings / Design calcs (this pack) / Manufacturer data (hangers, straps) / Eurocodes / TDCA deck guidance. ([Glenalmond Timber][6])

**Responsibilities & competencies**:

* Site supervisor, carpenters, banksman (as needed), competent person for lifting/plant (if used).

**Key hazards & controls (RAMS)**:

* Work at edges/water; slips/trips; power tools; manual handling; groundworks.
* Controls: barriers, non‑slip access, life ring at pond, cordon, tool guards, PPE, lifting plan if applicable. *(Use HSE risk‑assessment template to record hazards and controls.)* ([HSE][7])

**Materials & plant**:

* UC4 incised C24 framing; stainless or class 4 fixings; breathable membrane; DPC/EPDM; concrete pads; liner protection.

**Sequence (high level)**:

1. **Set out** deck footprint, pond aperture, and **pad locations**; confirm levels.
2. **Pads**: form 300×300×100mm concrete pads on compacted gravel; install DPC/EPDM isolation.
3. **Beams**: install outer and inner beams level/flush; **rebate inner beam** to seat top‑flange saddle hangers.
4. **Hangers & joists**: fix **saddle hangers** at inner beam; install joists; add **top straps** and **opposed toe‑screws**; face‑mount hangers at outer beam.
5. **Blocking & X‑bracing**: solid blocking at both beam lines; fit **galv. flat‑strap X‑brace** at outer edge; tension and fix.
6. **Liner interface**: form **anchor trench**, fold liner over inner beam face, backfill; add liner clamp/fascia **above waterline**.
7. **Decking**: lay 28×145 boards perpendicular to joists, **1–2% fall away from pond**, 5–6mm gaps, drip kerf near outer edge; cut flush; screw per manufacturer.
8. **Completion**: torque/fastener check; visual QA; area safe/clean.

> The steps mirror your Rev 3 build sequence so crews and reviewers see a direct line from design → method.

---

### B2) ITP (Inspection & Test Plan) — fill‑in table

*(Modelled on common UK ITP structure; add **H**old/**W**itness points where you want stop/go control. Keep evidence: photos, test records, check sheets.)* ([Consig][5])

| Activity / Stage   | Inspection / Test                 | **Acceptance criteria & reference**                                                                     | Freq | Responsible (C/S/BC*) | Records                  | HP/WP |
| ------------------ | --------------------------------- | ------------------------------------------------------------------------------------------------------- | ---: | --------------------- | ------------------------ | :---: |
| Set‑out            | Check grid, levels, pond aperture | Overall 5x5m, aperture 3x3m; line/square within +-5mm over 3m; levels <=+-5mm                           | 100% | C/S                   | Survey sheet, photos     |  WP   |
| Pads formed        | Dim./position check; bearing      | 300x300x100mm; centred under joist lines; founding on compacted granular; DPC/EPDM placed               | 100% | C/S                   | ITP check, photos        | **H** |
| Beams in place     | Line/level; fixings               | Tops **flush with joists**; rebates clean; fixings per manufacturer                                     | 100% | C/S                   | Check sheet              |  WP   |
| Inner beam hangers | Seat & fixings                    | Top‑flange saddle hangers rebated flush; fasteners per schedule; no damage to timber                    | 100% | C                     | Photo; datasheet mark‑up | **H** |
| Uplift restraint   | Straps + toe‑screws               | Strap type (LSTA or specified), tensioned; opposed toe‑screws (Ø6–8×120–160) high into beam             | 100% | C                     | Photos                   |  WP   |
| Joists             | Spacing/line                      | **47×150 C24 UC4 @ 400mm c/c**; cantilever 250mm beyond inner beam; blocking tight each beam line       | 100% | C/S                   | Check sheet              |  WP   |
| Outer beam         | Face‑mount hangers                | Installed to spec; **toe‑screw** option used if required to eliminate play                              | 100% | C                     | Photos                   |  WP   |
| Bracing            | X‑strap                           | Galv. flat‑strap (30–40mm×1–1.5mm), taut, fixings every other hole                                      | 100% | C                     | Photos                   |  WP   |
| Liner interface    | Protection & clamp                | Liner protected from metal edges; clamp/fixings **above waterline**; anchor trench backfilled           | 100% | C/S                   | Photos                   |  WP   |
| Decking            | Fixings, fall, gaps               | 28×145 boards; **1–2% fall away from pond**; 5–6mm gaps; drip kerf 10–15mm inboard; stainless fixings   | 100% | C/S                   | Check sheet              | **H** |
| Materials          | Certification                     | **UC4 incised** treatment certs; C24 grading; stainless/class‑4 fixings; product datasheets             |  Lot | C                     | Certs in Appendix        |   H   |
| Final QA           | Close‑out                         | Torque spot‑checks; snag‑free; area safe; as‑built photos                                               | 100% | C/S/BC                | QA form                  |   H   |

*C – Contractor; S – Supervisor; BC – Building Control (if involved)

The “acceptance criteria” above trace back to your spec (framing, hangers, bracing, liner details, decking fall/gaps) and the timber/durability choices you made.

---

## C) A couple of judgement calls to capture in your Design Basis (so reviewers don’t have to guess)

* **Imposed load category**: Is this a private domestic deck (Category A, typically **2.0 kN/m²**) or to be treated conservatively as “balcony/external” (consider **≥2.5 kN/m²**) because of edge exposure and potential crowding? Record the choice and why. ([Eurocodes][1])
* **Service class / durability**: Near‑pond timber is realistically **Service Class 3**; your spec already requires **UC4 incised** framing and stainless/class 4 fixings—state this explicitly.  
* **Checking level**: Note whether you want a peer **self‑check**, an **independent simple check**, or a more formal third‑party review (use SER/IStructE language for clarity). ([ser-ltd.com][2])
* **Temporary conditions**: For example, ensure **bracing/blocking** goes in before significant loading; identify any stages where uplift/restraint is not yet active.

---

## D) Ready‑to‑fill **Design Basis** text (drop this into Section 1–2 of your calc pack)

> **Project:** Pond deck – Option C low‑profile flush‑beam frame
> **Geometry:** 5 000×5 000mm deck, 3 000×3 000mm pond opening; 1 000mm walkway backspan; 250mm inward cantilever all sides.
> **Members:** Joists & beams C24 **UC4 incised** 47×150 @ 400mm c/c; 28×145 decking; solid blocking at both beam lines.
> **Connections:** Inner beam top‑flange saddle hangers rebated flush + top straps + opposed toe‑screws for uplift; outer beam face‑mount hangers; galvanised flat‑strap **X‑brace** at outer edge.
> **Codes:** EN 1990 (UK NA), EN 1991‑1‑1 (Table 6.2), EN 1995‑1‑1 (UK NA).
> **Actions:** **[Pick one]** Category A (2.0 kN/m²) / Balcony‑type (≥2.5 kN/m²) + finishes allowance. Combinations per EN 1990 Annex A1.
> **Service class / durability:** SC3; UC4 incised framing; stainless A2/A4 or class 4 fixings; cut ends resealed; drainage slope 1–2%.
> **Stability:** Deck diaphragm + blocking; outer beam **X‑brace** for lateral restraint; load path narrative included in Section 1.
> **Software/verification:** [List if used] with hand checks; checker identified; check level recorded.

---

## E) Why this aligns with “industry standard”

* The **structure of the calc pack** and its design summary is straight from **IStructE** guidance used for Building Control submissions in England & Wales.
* The **code references** and **NA choices** are exactly what **EN 1990** requires you to state for a defendable basis of design.
* The **imposed load category** decision and the **timber Service Class**/durability rules are grounded in **EN 1991‑1‑1** and **EN 1995‑1‑1**. ([Eurocodes][1])
* The “play‑by‑play” is expressed as a Method Statement + **ITP**, matching **HSE** expectations for RAMS‑style planning and common UK QA practice. ([HSE][4])

---

## F) Quick next steps

1. Paste the **worksheet template** into your calc doc and drop in the Option C numbers where I’ve put blanks—your Option C “Structural quick‑checks” already set out the tributary width and reaction order of magnitude, which will slot in neatly.
2. Copy the **Method Statement** and **ITP** tables into your project folder and assign names/dates/hold points.
3. Attach datasheets for the exact **hangers/straps/screws** you intend to use and reference them in the connection checks.
4. Have your structural friends perform and sign the **check section** (and state the check level). ([ser-ltd.com][2])

---

### (Appendix) What to attach in the pack

* GA and detail sketches; pad layout; rebate/hanger details; X‑brace route.
* Product datasheets and fixing schedules (hangers, straps, screws).
* Timber certificates (C24 grading; **UC4 incised** treatment).
* Photos for each ITP hold point (pads; hangers; straps; bracing; liner clamp; deck slope/gaps).
* Any risk assessments and the signed Method Statement (HSE RAMS expectation). ([HSE][7])

---

[1]: https://eurocodes.jrc.ec.europa.eu/sites/default/files/2022-06/EN1991_2_Malakatas.pdf?utm_source=chatgpt.com "Densities, self-weight, imposed loads for buildings - Eurocodes"
[2]: https://www.ser-ltd.com/ser-jersey/resources/guidance-notes/guidelines-for-checking?utm_source=chatgpt.com "7 - Guidelines for Checking the Structural Design of Buildings"
[3]: https://transportation.ky.gov/Organizational-Resources/Policy%20Manuals%20Library/Structural%20Design.pdf?utm_source=chatgpt.com "structural design guidance manual"
[4]: https://www.hse.gov.uk/construction/safetytopics/admin.htm?utm_source=chatgpt.com "Administration"
[5]: https://consig.org/wp-content/uploads/2018/04/18_04_13_CONSIG_ITP-Template_Rev-3.0.xlsx?utm_source=chatgpt.com "Inspection and test plan template - ConSIG"
[6]: https://glenalmondtimber.com/wp-content/uploads/2024/04/tdca-decking-handbook.pdf?utm_source=chatgpt.com "THE TIMBER DECKING HANDBOOK"
[7]: https://www.hse.gov.uk/simple-health-safety/risk/risk-assessment-template-and-examples.htm?utm_source=chatgpt.com "Risk assessment: Template and examples"
