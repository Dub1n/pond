# Pack C cutter-profile nesting

`generate_profiles.py` emits clean millimetre outer profiles for the current
Pack C material screen. The selected corner profiles are generated from
`clam.14.3_thick.svg` and `corner-web_thick.svg`, using each presentation
SVG's dashed Arrangement-E reference outline as the millimetre transform. It
deliberately excludes holes, washer circles, kerf, internal radii and drilling:
those remain fabrication-detail controls in the Pack C documents.

`profiles/corner-upper-pod-t30-df20.svg` is the separate cutter-reference
outline for the DF20 internal-web study. Its holes do not change purchased
sheet area, so the automated nesting job intentionally uses the outer contour
only.

Regenerate after changing a component outline:

```sh
./.venv/bin/python docs/packs/c/nesting/generate_profiles.py
```

The installed CLI is at `/home/gabri/apps/deepnest-cli`. Run it from that
directory because its worker module is resolved relative to its current working
directory. The job directory contains one SVG for every required part: nine
upper Hs, eighteen bridges, four upper pods and four lower webs.

```sh
cd /home/gabri/apps/deepnest-cli
node cli.mjs --timeout 15000 --bin 120,39.37 --output /tmp/pack-c-nest \
  /home/gabri/docs/pond/docs/packs/c/nesting/jobs/full-grp/*.svg
```

The numeric bin is interpreted as inches by this version of the CLI; this
1,000 mm-high run uses an oversized horizontal bin and the placed geometry
occupies approximately 1,491 x 1,000 mm. The checked-in profiles carry
millimetre dimensions. Pass only
SVGs: supplying `deepnest-mm.json` as an input makes this CLI fail. This
Deepnest fork can throw its `polygonArea` exception *after* it has written a
valid 35/35 nest; inspect `nesting-*/result.svg` and `data.json` rather than
treating that late error as an invalidation of the completed result. The
resulting contact nest is an **area screen only**.
Do not cut it directly: have the cutter apply at least 5 mm profile and edge
clearance, kerf compensation, radii and the documented hole/washer rules.

The preserved fixed-height 35/35 result is [`output/thick-grp-1000-high.svg`](output/thick-grp-1000-high.svg);
its machine-readable placements are beside it in `thick-grp-1000-high.json`.
