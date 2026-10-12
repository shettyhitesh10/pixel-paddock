# Helmet artwork, release 5

Original face artwork remains in `dist/assets/art/drivers-a.webp` through `drivers-h.webp` and `dist/artwork.js`. These files have not been replaced.

The helmet sheets are separate AI-assisted edits of the original images. They contain six columns and three rows, six animation poses per driver. The third row of sheet h is a generic driver and is intentionally not mapped to a profile.

The new global `window.PADDOCK_HELMET_ART` has the same person descriptor shape as the original artwork map. Integrating code can choose helmets by default and still retain the original map. Team principal artwork is unaffected.

Helmet colours are original fan interpretations inspired by recognizable driver palettes. They are not exact current-season sponsor or helmet designs. Generative editing can introduce small suit or gesture differences; the six-frame layout is preserved and was visually inspected.

`build_helmet_assets.py` copies the untouched generated PNGs here for future use and performs only WebP format encoding at quality 95. No resizing or cropping is performed. `provenance.json` records the original asset hashes, generated source paths and dimensions.
