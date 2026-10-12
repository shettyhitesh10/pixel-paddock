# Scheduled improvement instructions

This is the user's long-term Pixel Paddock F1 project. Preserve the original retro racing GAME interface: cobalt/navy instrument panels, yellow bitmap text, angular pixel borders, checkered details and original pixel artwork. The latest explicit user correction rejects actual photographs, white dashboard surfaces and modern non-pixel controls. Use the F1 Race / F1 Pole Position screen references in DESIGN_REFERENCES.md. Preserve all driver/team/principal pages, source attribution, vivid team palettes, detailed individual pixel faces, six-frame poses and signature labels. Never add photographs or randomize likenesses during refreshes. The latest user model preference is Astra. Do not claim that scheduled creation itself proves a run occurred.

## Opening a fresh cloud task

1. Read the Sites skill. Read the linked Site using its supplied project ID, preserving its existing audience and project ID. The identity in `.openai/hosting.json` must match that Site.
2. Acquire a fresh source repository write credential using the native Sites tool. Open the saved source through the Sites source helper when available. Never expose or write credential values to disk. The repository's `SCHEDULED_WORK.md`, `PROJECT.md`, and scripts are the durable instructions for future runs.
3. If bundled Sites source helpers are unavailable, use the native credential's remote URL and auth mode through a memory-only Git environment, keeping the credential in stdin/session memory. Clone the repository to an isolated workspace directory and keep its identity. Never create a replacement Site.

## Each run

1. Fetch a separate review candidate with `python scripts/refresh_data.py --community`; this writes research/refresh-candidate.json and does not update the released snapshot. Integrate only after checking session metadata, biography totals and event-specific UI labels. Review returned season and fetch dates. Keep the last successful snapshot when a publisher is unavailable. Never invent news, comments, standings or biographical facts. Use official team/F1 sources for roster/principal changes.
2. Review `PROJECT.md`. Complete one bounded, useful improvement from its ordered backlog. Prioritize observed bugs and weak source coverage. Keep the current experience usable and accessible.
3. Run checks appropriate to the change: JavaScript syntax, data ID/crosslink consistency, representative profile routes, source attribution and responsive browser checks when available. Record actual checks and any limits.
4. Update `dist/progress.html` with the date, concrete completed work, validation, source availability and next step. Update the roadmap. Keep prior report history. Do not mark work complete without evidence.
5. Push the exact source, package its configured static output, save and deploy that exact revision through Sites. Preserve the audience. Verify the deployment reaches a terminal successful state.
6. Return the deployed URL and progress-report URL, what improved, and any real blockers. Do not send messages to third parties or post community comments.

There is no published site or active recurring task yet. The reload button reads the saved data file; standalone HTML reloads its embedded snapshot. Treat snapshots as snapshots, and source errors as source errors.
