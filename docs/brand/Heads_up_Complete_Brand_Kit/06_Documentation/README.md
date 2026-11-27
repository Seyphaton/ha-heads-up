# Heads up - Complete asset build / release candidate

## Delivery status

This archive contains the assembled twelve-variant asset build, automated technical QA, rendered comparison sheets, original source reference, and reconstruction sources. It is delivered at the user's request for the ZIP download. It is **not an unconditional production-readiness certification**. Final separate design and product release reviews remain outstanding. Earlier layout approval is retained; it is not being treated as approval of reconstructed SVG fidelity or every new export.

## Included assets

- Main, Bright, Dark, Flat Blue, Flat White, Flat Navy, Transparent Light, Transparent Dark, Monochrome Black, Monochrome White, Warning, and Critical.
- SVG, PNG and lossless WebP; rounded-square and circular versions.
- 27 delivery sizes: 16, 20, 24, 32, 40, 48, 57, 60, 64, 72, 76, 80, 87, 96, 114, 120, 128, 144, 152, 167, 180, 192, 256, 384, 512, 1024 and 2048 pixels.
- Favicon ICO/SVG/PNG, Apple touch icon, Android-named icons and a web manifest.
- Supplied original banner, a localized updated version, and 1280 x 640 delivery assets.
- Original and extended palette definitions, compatibility assets and source archive.
- Rendered contact sheets, technical-validation.json and an asset hash manifest.

## Important source and fidelity distinction

The user-approved luminous Main, Warning and Critical PNGs are retained rather than replaced by newly rendered approximations. Their SVG counterparts are explicitly documented vector/gradient reconstructions from approved raster artwork. They are not recovered original vector masters, and their rendering is not pixel-identical to the PNGs. See 07_Quality_Assurance/approved-vs-vector.png and technical-validation.json. Do not silently replace the approved PNGs with exports from these SVGs.

The approved 2048-pixel luminous PNGs are upscaled from native 1088-pixel artwork. They do not contain newly recovered vector detail.

## Transparency and icon boundary

The luminous rounded-square tile, not the former surrounding image canvas, defines the icon boundary. PNG exteriors are transparent; no external canvas or halo is intended. Circular versions use a circle inscribed directly in the actual tile bounding square, without added padding. House, bell and severity badge geometry remains within that tested circle. This is not a claim of compliance with all operating-system adaptive-icon masks.

## Validation recorded in this build

The existing automated report records PASS, no errors, 1,615 raster files checked, 24 canonical SVGs checked, 666 lossless WebP pairs compared, and 162 approved delivery PNGs preserved byte-for-byte. These counts describe the validation run's scope, not the archive's total file count. Documentation and packaging metadata added at handoff are outside that image-validation run.

No live Home Assistant, iOS, Android, Safari or Firefox integration certification was performed. Small severity punctuation is not reliable as the sole indicator at 16-32 pixels. Use visible severity text and accessible names.

## Directory guide

01_Master: approved raster master and reconstructed SVG.
02_Icons: canonical variants and circular versions.
03_Favicons: browser and application icon assets.
04_Banners: supplied original and updated banner assets.
05_Color_Palette: color definitions and palette visuals.
06_Documentation: guidelines, changelog, path map and manifest.
07_Quality_Assurance: technical report, rendered evidence and review status.
08_Source_Reference: unmodified original ZIP.
09_Compatibility: preserved legacy naming and paths.
10_Build_Sources: working build scripts and geometry/gradient data.

Build scripts record the working process and may require path/environment adjustments to run outside the original workspace. They are not represented as a standalone installer.
