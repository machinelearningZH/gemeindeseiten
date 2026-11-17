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
- Pages builds generate a standalone static directory from both CSV files and `web/`
  into `_site/`; only HTML, CSS, JavaScript and CSV downloads are published. All asset
  paths are relative so GitHub project Pages and custom base paths work without Jekyll.
  The CSV files are authoritative; README tables are no longer maintained separately.
- The link checker lives in `src/municipalities/` and shares one HTTPX client
  across worker threads. It is packaged to expose `uv run check-links`; operator settings are
  validated from YAML, and relative CSV paths resolve from the configuration file.
  Use `uv run check-links`; the former root-level script has been removed.
- The Gemeindeamt directory dated 2026-07-01 lists 60 independent school municipalities
  (24 primary, 28 secondary, 8 combined). The cantonal school address directory also
  includes schools run by political municipalities and outdated domains; it is not
  a membership list. School links are stored separately without political municipality codes.
- School links were researched on 2026-10-26. The HTTP checker reached 106/120 URLs;
  both URLs for primary Andelfingen, Dänikon-Hüttikon, Wettswil, secondary Bonstetten,
  Seuzach, Uster, and Unteres Rafzerfeld returned HTTP 403. Their published school
  pages/navigation confirm the URLs; do not replace them merely to make the checker green.
  Dielsdorf's secondary site requires JavaScript (its public JSON API confirms the
  collection); Höri and secondary Stadel load documents through session-bound AJAX.
  Stadel's default download folder is its systematic law collection. Laufen-Uhwiesen
  links directly to a public SharePoint folder; Obfelden-Ottenbach links to its
  SharePoint law collection from the downloads page.
- The weekly checker stores JSON/Markdown as Actions artifacts and compares against
  the last successful default-branch report. Missing history yields `uncompared`,
  never an assertion that a failure is new. HTTP 403/429 are blocked checks; HTTP
  success says nothing about content. Builds and automated checks do not advance
  the manual research dates shown on the site.
- The document pilot adds two optional political-municipality CSV fields, both covered
  by the weekly checker. Blank cells mean not captured, not absent. Use official detail
  pages where available; Horgen and Wetzikon publish these links directly as PDFs,
  which may need replacing when new files are published. Kloten and Winterthur use
  JavaScript-based LexWork law pages. No source or review-date fields are displayed.

## 2026-10-26: eMudhra/emSign certificate update

Require certifi >=2026.10.19; only certifi and affected pip changed package versions. Keep the seven-day cooldown. Remove only the incident certifi exception after 2026-10-27 03:24:17 Europe/Zurich, then relock and sync. Build/CI uv pins are 0.13.5; Python image stages patch existing pip with secure uv. Deployment images still require a fresh build (`--pull --no-cache`) and verification before redeployment. Advisory: https://discuss.python.org/t/109576.
