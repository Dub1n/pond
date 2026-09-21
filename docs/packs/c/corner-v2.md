# Pack C corner v2 — split-plate corner seat

> **Superseded.** The current one-piece aluminium corner is
> [corner v3](corner-v3.md). Retain this document as design and calculation
> history only.

## Status and scope

Corner v2 was the selected split-GRP prototype corner before corner v3. It
replaced the earlier monolithic pod in [corner-v1.md](corner-v1.md) and is now
retained to record that geometry, load path and proof basis.

Nothing here approves batch fabrication or deck loading. The delivered GRP,
complete wet corner, basket interface, C2 sling and deck reactions still need
the stated physical proof.

## Components and material

Each of the four corners contains:

| Part | Quantity per corner | Current material |
| --- | ---: | --- |
| Mirrored upper corner plate | 2 | 9.5 mm structural pultruded GRP flat bar |
| Thick lower corner web | 1 | 9.5 mm structural pultruded GRP flat bar |
| Rail/corner fastener stack | 6 | M8 A2-70 bolt, two 25 mm A2 washers, nyloc and internal 304 crush sleeve |
| Separate C2 post stack | 2 | M8 x 50 A2-70 bolt, 16 OD x 8.4 ID x 20 mm nylon spacer, 30 mm roof washer, 25 mm underside washer and nyloc |
| Low basket-bearing spacer | 1 nominal | Sealed 9.5 mm GRP offcut, sized from the real basket bearing feature |

The upper plates are the supplied shapes in `diagrams/corner-rework/`. Each is
about 353.55 x 157.33 mm in its 45-degree stock orientation. The unchanged
thick lower web is about 353.53 x 197.48 mm in its 45-degree stock orientation.
The lower-web fit in nominal 200 mm stock has only about 2.5 mm total width
margin and therefore depends on the measured bar and cutting method.

## Geometry

Use local rail axes intersecting at `(0,0)`. The six rail/corner axes remain:

- `(55,0)`, `(125,0)` and `(195,0)` on one rail; and
- `(0,55)`, `(0,125)` and `(0,195)` on the other.

Both upper plates and the lower web share the two 55 mm axes. One upper plate
continues along each rail chain to the four 125/195 mm axes. The two upper
plates overlap across the strengthened inner diagonal and use the shared 55 mm
bolts to act as a connected pair.

The separate lower C2 post axes are approximately `(-140,55)` and `(55,-140)`.
They are not rail/corner bolts. Their centre spacing is 275 mm.

The four basket-retention axes remain separate M6 positions. Before issuing a
cutting template, retain at least 16 mm from every M6 axis to a GRP edge and
prefer the former R20 local land. The supplied split outline has only about
10.5 mm at two single-ply outer basket axes and must be locally widened there.

## Corner basket

The default corner basket is centred at `(0,0)` and rotated **45 degrees** in
plan. The combined upper plates provide an effective minimum support envelope
of approximately 275 x 293 mm. Use the smaller B23 basket at corners where it
meets the planting schedule; this gives the clearest route around the C2 posts
and sleeved cord turns.

The larger rigid basket is correctly named **B27**: its listed outside side is
270 mm, not 280 mm. The 275 mm C2-post spacing and 275 x 293 mm support envelope
are axis/support geometry, not a clearance envelope. They do not include the
16 mm posts, 30 mm roof washers, chafe sleeve, knot, cord exit tangent, basket
taper or removal travel. Use a full-size template and the real basket before
assigning B27 to a corner.

If an otherwise acceptable B27 only conflicts at an unloaded plastic basket
corner, either of these remains a prototype contingency:

- trim and fully smooth only the non-structural corner material not required
  to retain the PB25 cartridge; or
- make a smooth reinforced opening in the **plastic basket**, not the GRP
  corner plate, and pass the C2 cord through a replaceable soft sleeve.

The cartridge must remain clear of the modified area, the basket must retain
its shape and contents, and the cord must not be pinched or forced to change
direction. A modification is accepted only after wet removal, one-corner
uplift and snag tests. It is not included in the nominal design or purchase
count.

Because the two upper plates form a one-ply/two-ply step, one basket bearing
point is one plate thickness low. A sealed 9.5 mm GRP offcut spacer brings that
point to the common bearing plane. The spacer is a broad bearing pad, not a
stack of washers, and does not replace any basket-retention fastener.

## Load paths and screens

Normal basket gravity bears through the reinforced basket base, the two upper
plates and the low-point offcut spacer into both rail legs. The four M6 basket
fasteners retain the empty rigid basket against handling and uplift; they do
not suspend its planted service load.

Each C2 leg loads its own upper plate and transfers to the neighbouring 55 mm
rail axis through a continuous plate path. The revised direct span is about
140 mm. Matching the former 33.3 MPa isolated-strip comparison needs about
83.9 mm width; the supplied silhouette measures about 117.7 mm through the
middle and screens at about 23.7 MPa.

The two shared 55 mm axes combine upper-plate, lower-web and rail-tube duties.
A deliberately pessimistic 0.763 kN corner action plus complete 0.30 kN C2
proof action gives about 17.2 MPa nominal bearing against a 6.5 mm effective
diameter in one 9.5 mm ply. This is below the dry 70 MPa E23 comparator, but
does not prove wet bearing, bedding or load sharing.

The unchanged lower web retains the earlier plate-path screen. The split upper
pair must not inherit the monolithic `clam.14.3_thick` plate-only stiffness
result: its two local inner links and shared bolts form a plausible parallel
path, but connection slip and plate-to-plate bearing now matter. The complete
wet joint must still demonstrate at least 20 kN m/rad from 0 to 60 N m after
bedding, plus the retained 30 N m roll and deliberately unequal C2 loading.

## Release gates

Corner v2 remains a prototype until all of the following are recorded:

- delivered flat-bar thickness, width, fibre direction and permanent-
  freshwater suitability;
- full washer footprints and the widened outer M6 basket lands;
- a complete two-upper/one-lower rail joint with measured crush sleeves and
  no whitening, crushing, progressive slip or tube damage;
- dry and wet corner stiffness, roll, eccentric basket, unequal C2-leg and
  complete-C2-sling-loss tests;
- B23 and any proposed B27 corner template with posts, washers, knots, chafe,
  cartridge and removal travel present;
- accepted low-point spacer bearing and one-corner basket uplift; and
- flexible-ring and deck reactions using the measured corner behaviour and
  cord tangents.
