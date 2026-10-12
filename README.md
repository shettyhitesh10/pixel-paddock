# Pixel Paddock — release 4

Open `pixel-paddock-v4.html` directly in a browser. It embeds all artwork, the original pixel font, captured data and the build report; no server is needed. The `dist/` folder is the equivalent static website.

The UI follows a retro racing-game cabinet: detailed pixel character selection, colour-coded garages, a Singapore night circuit, timing screens and an original bitmap typeface. No driver photographs are used.

## Coverage

- 22 current drivers and one former season entrant, 11 teams, 13 leadership roles: 47 profiles.
- 36 animated pixel characters, six frames each; original team car illustrations.
- 23 race files; Singapore race, qualifying and Sprint classifications.
- Official post-Singapore championship snapshot checked 12 October 2026, 11 linked articles and 5 sourced public comments. Dates are retained per source.
- Search, filters, favourites, private local notes, keyboard driver selection and reduced motion.

## Validate and export

```sh
node --check dist/app.js
node scripts/check_retro.cjs
python scripts/build_report.py
python scripts/export_html.py
```

The check suite exercises templates and event handlers in a simulated DOM. It does not verify browser layout, actual CSS animation playback or browser persistence. Chromium could not launch under this execution sandbox. Hosting and scheduling remain pending.

## Data maintenance

`refresh_data.py --community` fetches a separate review candidate into `research/refresh-candidate.json`. It never overwrites the reviewed snapshot. Review the session context, source timestamps, biographies and matching UI labels before integrating candidate data. Failed sources retain their previous records; unknown roster IDs and older championship rounds are rejected. The UI reload button reloads the saved file, not a live sports API.

Current standalone: about 7.4 MB, including 14 embedded WebP assets. The source PNGs are retained separately in the workspace; see `research/artwork-v4-provenance.json`. Artwork compression preserves original dimensions and composition.
