# Data pipeline and automatic updates

The frontend POC reads a versioned snapshot. Driver dossiers are event records, separate from artwork and page templates. The next backend can produce the same shape without rewriting the driver pages.

## Current working path

1. Verified source facts live in `data/sources/2026-singapore.json`. Raw published figures, short sourced notes, and available radio excerpts retain source URLs and capture dates.
2. `python scripts/build_driver_weekends.py` joins those facts to classifications, computes comparisons, and fills `driverWeekends` in the website snapshot. It rejects mismatched events and incomplete driver coverage.
3. The frontend renders timing, strategy, radio and AI assessment from each dossier. Missing radio and tyre data remain explicitly missing.
4. Export the same data into the portable HTML with `python scripts/export_html.py`.

Timing comparisons use the deepest qualifying stage both teammates completed. Race finish gaps are calculated only for finishers on the same lap. Fastest laps are shown as raw figures, not adjusted race pace. Pit-lane duration includes transit; stationary stop duration must use a separate provider field. Stint boundaries derived from pit records are labelled. A retired driver may still have a classified position.

## Fetch adapter prepared for future use

`collect_openf1.py` collects a pinned race and qualifying session into a separate candidate. It validates that they belong to the same meeting, rate-limits requests, retains endpoint errors, and never overwrites the approved website snapshot.

```sh
python scripts/collect_openf1.py --race-session-key RACE_KEY --qualifying-session-key QUALI_KEY
```

Replace the placeholders with numeric keys from the [OpenF1 sessions API](https://openf1.org/docs/#sessions). Endpoints cover laps, pit records, stints, radio, race control, classifications and grid. Historical data is available without authentication; live data requires provider access. No credential belongs in browser code.

The network fetch could not run in this execution sandbox. Adapter behavior is checked with provider-shaped fixtures, not claimed as a successful live refresh.

OpenF1 returns selected audio recordings, not full radio transcripts, and [documents reduced 2026 coverage](https://openf1.org/docs/#team-radio). Empty responses must be represented as unavailable. A future transcription worker should retain clip URL, timestamp, language, confidence and any human corrections; a transcript must never be generated from the finishing order.

## Before enabling unattended population

- Add a provider normalizer from the candidate to this event dossier contract; validate driver identities against the event roster rather than guessing from names.
- Keep immutable raw captures and per-section freshness. Reject wrong seasons, meetings and older classifications. On endpoint failure, retain the last valid section with its actual date.
- Use lap and stint data to compare representative pace with pit laps, Safety Car periods and traffic excluded. Keep raw and adjusted values distinct.
- Generate AI stories in a server worker using a bounded evidence bundle: timing, incidents, strategy and selected radio. Store evidence links, model/version, generation date, confidence and separate facts from judgment. Current stories are AI-authored local assessments, not an autonomous model service.
- Make the dashboard and race centre event-driven before publishing the next race; the current hero still presents the Singapore capture.
- After validation, atomically write a new snapshot and rebuild the HTML. Then add a scheduler. No polling, hosted backend or recurring job is active in this POC.

No public comments are posted by this pipeline. Personal notes stay local to the browser.
