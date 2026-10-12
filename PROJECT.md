# Project roadmap — release 5

Preserve the approved retro game interface, detailed pixel assets and original character sheets. Current driver artwork uses helmets. The user requested GitHub storage first, then a local frontend POC; keep hosting and autonomous data updates for later work.

## Completed in this revision

- Preserved approved release 4 in GitHub commit b0409c5cda21b8161cfc40c7171ac2e971b4b85e.
- Added 23 helmeted driver characters; original faces and principals retained.
- Added 22 weekend dossiers: timing, strategy, radio coverage, AI story and teammate comparison. Former entrants are not assigned invented weekend data.
- Source facts separated from derived analysis; comparison semantics and failure handling tested.
- Historical OpenF1 collector and an explicit path toward autonomous population prepared.
- Portable HTML and build report updated.

## Next work

1. Inspect the local POC in a real browser and fix observed layout/interaction issues.
2. Normalize provider candidates into the event dossier contract and make the overall race centre/dashboard event-driven.
3. Expand sourced radio/tyre coverage; add verified audio and corrected transcripts when available.
4. Add representative lap-by-lap pace, race-control incidents and stint comparisons with context filters.
5. Add evidence-grounded server-generated AI stories with provenance and review controls.
6. Add validated automatic snapshot updates and then a scheduler/backend.

Keep missing data explicit. Distinguish pit-lane transit from stationary stop duration, qualifying classification from actual grid, and mechanical retirement from driver error. No model credential belongs in the frontend.
