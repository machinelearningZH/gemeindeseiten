# NOTES

Essential insights and (non obvious) findings gathered during coding work.

- Typer enables styled help on GitHub Actions. CLI text assertions must strip
  ANSI sequences with `Text.from_ansi(...).plain` before matching option names or summaries.
- Municipal website and law collection links were checked on 2026-10-23. Collection
  entry pages are retained where the website automatically opens its first chapter
  (Kleinandelfingen, Nürensdorf and Hombrechtikon).
- Volken's “Systematische Rechtssammlung” navigation redirects to its history page.
  The CSV instead uses the municipality-filtered ePublikation link published under
  “Gemeinde” in that same navigation.
- Pages builds stage only README.md (as index.md) and the CSV, keeping repository
  source files out of the published site. After recreating
  `machinelearningZH/gemeindeseiten`, Pages was confirmed disabled and no workflows
  were uploaded on 2026-10-23. Enable Pages again with GitHub Actions as the source
  and choose the site's visibility; the workflow derives the base path automatically.
- The link checker lives in `src/municipalities/` and shares one HTTPX client
  across worker threads. It is packaged to expose `uv run check-links`; operator settings are
  validated from YAML, and relative CSV paths resolve from the configuration file.
  Use `uv run check-links`; the former root-level script has been removed.
