# Pixel Paddock — release 5 local POC

A retro F1 companion with pixel character selection, team-colour garages, race timing screens and driver weekend dossiers.

## Open locally

The source works without a framework or dependency installation:

```sh
python -m http.server 8000 --directory dist
```

Open http://localhost:8000 in your browser. To make a portable, fully embedded HTML:

```sh
python scripts/build_report.py
python scripts/export_html.py
```

Open `pixel-paddock-v5.html`. The approved prior `pixel-paddock-v4.html` remains available, and release 4 is preserved in Git history.

## Driver pages

- Timing: Q1/Q2/Q3 laps, starting grid or pit-lane start, race/Sprint classification times, fastest lap and points.
- Strategy: pit-entry laps, pit-lane duration, a derived stint timeline and sourced tyre compounds where verified.
- Radio: available published excerpts and reported summaries, clearly labelled. Missing recordings stay missing.
- AI story: source-linked subjective assessment, reported incidents/turning points and a critical comparison with the teammate.

All 22 current drivers have dossiers; the former season entrant is marked not entered for this event. There are 47 entity profiles in total.

## Artwork retained

`dist/helmet-artwork.js` selects six-frame helmeted fan interpretations for 23 drivers. `dist/artwork.js` and all original face sheets remain unchanged for future use. Principal characters retain their original art. Helmets are stylised interpretations, not exact reproductions of every current helmet edition.

## Checks

```sh
node --check dist/app.js
node scripts/check_retro.cjs
python scripts/test_weekend_pipeline.py
```

Source, template, handler and offline ingestion checks pass. Real browser rendering, mobile overflow, actual CSS playback and browser persistence remain unverified because Chromium is blocked in the execution sandbox.

## Data and future updates

Official Singapore timing, starting-grid, fastest-lap and pit-stop records were checked on 12 October 2026. Each section keeps its own retrieval date; radio covers selected published material, not a complete archive.

See [the data pipeline plan](docs/DATA_PIPELINE.md). `build_driver_weekends.py` already normalizes verified event facts into the frontend’s dossier format. `collect_openf1.py` prepares historical source candidates with pinned session keys and partial-failure handling; its live network path remains unverified in this sandbox. No autonomous fetcher, hosted backend, AI service or scheduled job is active in this POC.

Original PNG artwork remains in the working asset archive. The current and legacy encoded assets are retained in source control; the source scripts do not regenerate AI images on their own.
