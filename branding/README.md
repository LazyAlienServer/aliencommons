# AlienCommons branding

This directory contains the source and canonical exports for the AlienCommons
brand mark. Product code should consume copies generated from these files rather
than treating an application-specific asset as the design source.

## Structure

```text
branding/
├── source/
│   └── logo.aseprite          Editable 32 × 32 pixel-art source
├── logo-mark.svg              Canonical scalable logo mark
├── logo-mark-32.png           Native-size raster export
├── logo-mark-64.png           2× raster export
├── logo-mark-128.png          4× raster export
├── logo-mark-256.png          8× raster export
├── logo-mark-512.png          16× raster export
└── web/
    ├── favicon.svg
    ├── favicon.ico
    ├── favicon-16.png
    ├── favicon-32.png
    ├── favicon-48.png
    ├── apple-touch-icon.png
    └── pwa/
        ├── icon-192.png
        ├── icon-512.png
        ├── icon-maskable-192.png
        └── icon-maskable-512.png
```

GitHub-specific presentation assets live separately in `.github/assets/`.
The current `logo-lockup.png` is a 1280 × 640 horizontal brand card combining
the logo mark with an Alegreya Medium wordmark. It is used at the beginning of
the repository READMEs and can also be uploaded as the repository social preview.

Brand assets are covered by the separate terms in [`LICENSE`](LICENSE), not by
the repository's MIT License.

## Export rules

- Treat `source/logo.aseprite` as the editable source of truth for the logo mark.
- Keep the native artwork on its 32 × 32 pixel grid.
- Scale raster exports by integer multiples with nearest-neighbour sampling.
- Keep `logo-mark.svg` transparent and preserve crisp pixel edges.
- Regenerate web icons from the canonical mark instead of editing them independently.
- Use `#4B3832` as the established solid brand background where one is required.

## Terminology

- **Logo mark**: the standalone book-and-laurel symbol.
- **Wordmark**: the typeset `AlienCommons` name.
- **Logo lockup**: the logo mark and wordmark arranged as one composition.
- **Social preview**: a fixed-size presentation image used when sharing a link.
