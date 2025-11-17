# Appendix A – Key Design Factors & Material Data  

===============================================  

## 1. Actions / combination factors (EN 1990 + UK NA)  

| Parameter                         | Value       | Notes                                                                              |
| --------------------------------- | ----------- | ---------------------------------------------------------------------------------- |
| γG (permanent, unfavourable)      | 1.35        | UK NA Table NA.A1.2(B) [oaicite:1].                                                |
| γQ (variable leading)             | 1.50        | UK NA Table NA.A1.2(B) [oaicite:1].                                                |
| ψ₀ (accompanying variable)        | 0.70        | Balcony/external category (Table 6.1 EN 1990 / UK NA) [oaicite:1].                 |
| ψ₁ (frequent)                     | 0.50        | Balcony/external category (Table 6.1 EN 1990 / UK NA) [oaicite:1].                 |
| ψ₂ (quasi-permanent)              | 0.30        | Balcony/external category (Table 6.1 EN 1990 / UK NA) [oaicite:1].                 |
| Deflection limit (serviceability) | L/250       | Adopted for external deck walking area; state in Design Basis.                    |
| Imposed load Qk                   | 3.0 kN/m²   | Balcony/terrace category for robustness (see Design Basis note).                  |

## 2. Timber material / design modifiers (EN 1995‑1‑1 + UK NA)  

| Parameter                                   | Value        | Notes                                                             |
| ------------------------------------------- | ------------ | ----------------------------------------------------------------- |
| Service class                               | SC3          | External, adjacent to water.                                      |
| kmod (permanent)                            | 0.50         | Table 3.1 for SC3, permanent [oaicite:2].                         |
| kmod (medium-term)                          | 0.70         | Table 3.1 for SC3, imposed load duration [oaicite:2].             |
| kmod (short-term)                           | 0.90         | Table 3.1 for SC3, short-term [oaicite:2].                        |
| kmod (instantaneous)                        | 1.10         | Table 3.1 for SC3, instantaneous [oaicite:2].                     |
| kdef                                        | 2.00         | UK NA Table 3.2 for SC3 [oaicite:3].                              |
| γM for timber (solid)                       | 1.30         | UK NA material factor for solid timber [oaicite:3].               |
| Characteristic bending strength, fm,k (C24) | 24 N/mm²     | EN 338 strength class table [oaicite:4].                          |
| Characteristic shear strength, fv,k (C24)   | 2.5 N/mm²    | EN 338 strength class table [oaicite:4].                          |
| Mean modulus of elasticity, E₀,mean (C24)   | 11 000 N/mm² | EN 338 strength class table [oaicite:4].                          |

## 3. Ground / bearing assumptions  

| Parameter                              | Value     | Notes                                                                            |
| -------------------------------------- | --------- | -------------------------------------------------------------------------------- |
| Allowable bearing pressure on sub-base | 200 kN/m² | Conservative assumption for compacted granular fill; replace with site data if available. |
| γG (ground bearing)                    | 1.35      | Use unless geotechnical guidance dictates otherwise.                             |

## 4. Corrosion / durability  

- Fasteners/hangers/straps: Stainless steel A2 or A4, or hot-dip galvanised Class 4 to suit UC4 incised timber and SC3 exposure.  
- Confirm compatibility between fixings and timber treatment (UC4).  
- Reseal all cut ends of framing; keep fixings above waterline at liner interface.

## 5. Connection / fixing data (enter from sourced manufacturer tables)  

| Item                                      | Value (enter)            | Notes                                                             |
| ----------------------------------------- | ------------------------ | ----------------------------------------------------------------- |
| Saddle hanger shear/bearing capacity      | <enter>                  | From manufacturer datasheet for inner beam hanger and fasteners.  |
| Face-mount hanger shear capacity          | <enter>                  | From manufacturer datasheet for outer beam hanger and fasteners.  |
| Uplift strap (LSTA-type) tension capacity | <enter>                  | Include strap grade and screw/nail pattern.                       |
| Toe-screw withdrawal (Ø6–8 × 120–160)     | <enter>                  | From fastener manufacturer for C24, used for uplift/anti-roll.    |
| Flat-strap X-brace axial capacity         | <enter>                  | Fixings every other hole; state screw type/grade.                 |

## 6. Decking span data (28 × 145 @ 400 mm c/c)  

- Enter supplier span table value confirming 400 mm c/c is acceptable under 3.0 kN/m² and deflection limit L/250: **<enter span verification>**.  
- If decking species differs, record the specific span rating and any adjusted limit.

---

Notes:  

- Insert the manufacturer/supplier values in Sections 5–6 from your sourced data.  
- The code factors above are fixed inputs for the Option C Design Basis.  
- File is to be appended to the Structural Calculation Pack and cited in the Design Summary.  

## oaicite reference index

**oaicite:1** — [EN 1990 / UK NA factors (γG, γQ, ψ) – summary](https://www.newsteelconstruction.com/wp/wp-content/uploads/2013/01/Tech1301NSC.pdf)  
**oaicite:2** — [EN 1995-1-1 Table 3.1 (kmod) – SC3 entries](https://gaprojekt.com/wp-content/uploads/2021/11/Eurocode-5-Design-of-timber-structures.pdf)  
**oaicite:3** — [UK NA to EN 1995-1-1 (kdef, γM for solid timber)](https://archive.org/download/bs.na.en.1995.1.1.2008/bs.na.en.1995.1.1.2008.html)  
**oaicite:4** — [EN 338 C24 strength class data (fm,k, fv,k, E0,mean)](https://download.infograph.de/man_en/en1995_timber_checks.pdf)  
