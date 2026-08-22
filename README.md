# STO Ship DB

A single-page web app for filtering and sorting **Star Trek Online** Tier-6 starships
by their attributes and bridge officer abilities. Data is pulled **live** from a public
Google Sheet, so the site stays current without redeploying.

> Initially made by Reddit user [u/wkrick](https://www.reddit.com/user/wkrick), now
> rebuilt and maintained by **@jalification**, using data from the
> [Sortable/Filterable T6 Ship List v2](https://docs.google.com/spreadsheets/d/1SSsxWmE8Oz35D6MvLheFNUfhWerHNkUGOGtjxLlrTuA)
> by Reddit user [u/Fleffle](https://www.reddit.com/user/Fleffle).

**Live demo:** _add your Netlify URL here_

---

## Features

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
