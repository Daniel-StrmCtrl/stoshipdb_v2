# STO Ship DB

A single-page web app for filtering and sorting **Star Trek Online** Tier-6 starships
by their attributes and bridge officer abilities. Data is pulled **live** from a public
Google Sheet, so the site stays current without redeploying.

> Initially made by Reddit user [u/wkrick](https://www.reddit.com/user/wkrick), now
> rebuilt and maintained by **@jalification**, using data from the
> [Sortable/Filterable T6 Ship List v2](https://docs.google.com/spreadsheets/d/1SSsxWmE8Oz35D6MvLheFNUfhWerHNkUGOGtjxLlrTuA)
> by Reddit user [u/Fleffle](https://www.reddit.com/user/Fleffle).

**Source code:** <https://github.com/Daniel-StrmCtrl/stoshipdb_v2>
**Live demo:** _add your Netlify URL here_

> **Open project.** This is open source — anyone is free to copy, fork, and keep it
> running. If the current maintainer is ever unable to continue, please feel free to
> take it over so the community can keep using it.

---

## ⚠️ Heads up: this is "vibecoded"

Much of this project — especially the Pivot tab, the tabbed UI, the colour-coding, and
the backup tooling — was built quickly and iteratively with an AI coding assistant
("vibe coding"): describe what you want, look at the result, adjust, repeat. That got a
working, useful tool fast, but it means you should treat the code with appropriate
caution rather than assume it's production-hardened. Known risks and caveats:

- **Limited testing.** There is no automated test suite. Behaviour was verified by
  eyeballing the running app and spot-checking numbers against manual calculations, not
  by exhaustive tests. Edge cases may be wrong.
- **Data-shape assumptions.** The app depends on the source spreadsheet keeping its
  current column layout and value conventions. If the sheet's columns are reordered,
  renamed, or change format, parsing can silently produce wrong results rather than
  fail loudly.
- **Derived data may be imperfect.** Seat layouts, the Science-Destroyer split, and the
  bridge-officer matcher are re-derived in code. They match the reference behaviour as
  far as it was checked, but subtle cases haven't all been proven correct. Don't treat
  the numbers as authoritative for anything important without verifying.
- **Undocumented dependency.** Live data comes from Google Sheets' unofficial `gviz`
  endpoint, which could change or break without notice (see *Notes & limitations*).
- **Review before you rely on or extend it.** If you fork this or build on top of it,
  read the code first, add tests where it matters to you, and validate outputs against a
  known-good source. Contributions that harden it (tests, validation, error handling)
  are very welcome.

In short: it's a fan tool made for convenience, not a source of truth. Use it, enjoy it,
but sanity-check anything that matters.

## Features

The app is organised into three tabs: **Filter**, **Pivot**, and **About**.

### Filter tab

- **Ship Attributes filter** — filter on any of 50+ attributes (Faction, Hull/Shield
  modifier, seats, consoles, weapons, traits, etc.) with `=`, `≠`, `>`, `≥`, `≤`, or
  `Contains`. Add multiple filters (combined with AND).
- **Bridge Officer Abilities filter** — pick a Type → Ability → Level and the app finds
  every ship that can actually slot it, honouring bridge-officer seat ranks,
  specializations, and universal seats (a real per-seat assignment, so requesting two
  abilities requires two suitable seats).
- **Release year filter** — filter ships by the year they were released.
- **Additional result columns** — add any attribute (including **Release Date**) as an
  extra column in the results.
- **Sorting** — click any column header to sort; numeric columns sort numerically and
  the Release Date column sorts chronologically. The default view is **newest first**.
- **Science Destroyer modes** — ships with Tactical/Science modes are listed as two
  distinct entries so seat-based filtering is accurate.

### Pivot tab

Heatmap summary tables computed **live** from the same ship data (they refresh when the
sheet does):

- **Weapons — Fore × Aft** — ship counts by fore vs aft weapon count.
- **Ship Types** — count of ships per type (Cruiser, Escort, Science Vessel,
  Dreadnought Cruiser, …), sorted by count, flowing into multiple columns on wide
  screens.
- **Specializations — Primary × Secondary (4 & 3)** — ships with exactly one rank-4 and
  one rank-3 specialization seat, cross-tabulated by primary (rank 4) and secondary
  (rank 3) spec. Rendered for all ships plus four subsets: **experimental weapon**,
  **hangar bay**, **secondary deflector**, and **plain ships** (none of those three).
  Specialization names are colour-coded (Cmd/Int/Pil/Tmp/MW), and each table lists the
  combinations that currently have **zero ships** ("missing combinations").

### About tab

Credits, the Science-Destroyer counting note, and the source-code link.

## How it works

Google Sheets exposes a public read endpoint (`gviz`) for any sheet shared as
"Anyone with the link." On load, the page:

1. Renders instantly from an **embedded snapshot** baked into `index.html`.
2. Fetches the sheet in the background, transforms it into the app's data model
   (deriving seats, boff seat layouts, the Science-Destroyer split, etc.), and
   **caches the result in `localStorage` for 24 hours**.

So each visitor triggers at most one sheet fetch per day, the UI is instant, and
editing the spreadsheet updates the site within a day with no redeploy. There is no
server, no build step to view it, and no API key.

**Resilience layers**, in order: live sheet → 24 h browser cache → embedded snapshot in
`index.html` → raw `build/sheet_backup.json` (plus full git history). If the live sheet
is slow or down, visitors still see the embedded snapshot; if the sheet disappears
entirely, the site can be rebuilt from the saved backup (see *Rebuilding* below).

The sheet is configured near the top of the `<script>` in `index.html` (and in
`build/template.html`):

```js
const SHEET_ID = "1SSsxWmE8Oz35D6MvLheFNUfhWerHNkUGOGtjxLlrTuA";
const GID = "1249626217";
```

## Deploying

It's a single static file — host `index.html` anywhere.

- **Netlify (drag & drop):** drag `index.html` onto <https://app.netlify.com/drop>.
- **Netlify (from Git):** connect this repo — the included `netlify.toml` sets the
  publish directory (repo root) and caching/security headers, with no build command.
  Every push redeploys.
- Any static host works the same way (GitHub Pages, Cloudflare Pages, Vercel, …).

Updating the **spreadsheet** never requires redeploying — the data is fetched live.
You only redeploy if you change `index.html` itself.

## Rebuilding the embedded snapshot

The embedded snapshot in `index.html` is a fallback for instant first paint and
offline resilience; live data always refreshes on top of it. To regenerate it (or after
editing `build/template.html`):

```bash
cd build
python3 build_seed.py   # fetch the sheet -> appdata.json (needs internet, Python 3)
python3 build.py        # inject appdata.json into template.html -> ../index.html
```

- `build/template.html` — the source HTML/CSS/JS (with `__APPDATA__` / `__BUILD_DATE__`
  placeholders). **Edit the app here**, not in the generated `index.html`.
- `build/build_seed.py` — fetches the sheet and derives the data model + attribute
  catalog into `appdata.json`.
- `build/build.py` — injects the data and today's date into the template.
- `build/sheet_backup.json` — a complete backup of the raw sheet, refreshed on every
  successful `build_seed.py` run. If the Google Sheet ever disappears, `build_seed.py`
  automatically falls back to this file, so the site can still be rebuilt from the last
  saved copy. Git history keeps every past version as a dated archive.

## Notes & limitations

- The sheet is publicly readable; anyone viewing the site can reach the raw data. Fine
  for a fan ship database — don't put anything private in that tab.
- The `gviz` endpoint is undocumented but has been stable for years. If it ever breaks,
  the fix is moving to the official Google Sheets API v4 (which needs an API key).
- Science Destroyers' per-mode **power-bonus** values aren't present in the source
  sheet, so both modes show the sheet's value; all other per-mode stats (seats,
  features, seat counts) are derived exactly.
- Ship, trait, and console names link to [STO Wiki](https://stowiki.net).
