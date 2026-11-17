# NOTES

Essential insights and (non obvious) findings gathered during coding work.

- Cantonal laws use ZH-Lex's published current-version links
  (`https://www.zhlex.zh.ch/Erlass.html?Open&Ordnr=…`). Keep these rather than
  version-specific detail pages or PDFs, which can point to superseded texts.

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
- The two optional political-municipality document URL fields are covered by the
  weekly checker. Blank cells mean no link could be verified, not that a document
  does not exist. Use official detail
  pages where available; Horgen and Wetzikon publish these links directly as PDFs,
  which may need replacing when new files are published. Kloten and Winterthur use
  JavaScript-based LexWork law pages. No source or review-date fields are displayed.
- For ePublikation, verify the publication ID, title, `PUBLISHED` state and publishing
  entity using its public `/api/v1/publications/{id}` record; town names alone also
  match schools. Use the public `#!/search/publications/detail/{id}` link. The HTTP
  checker sees the JavaScript shell, so it cannot detect removal of a hash-routed record.
- Mixed Besoldungsverordnungen qualify as Personalrecht only when the published text
  actually covers municipal staff. Authority-only compensation and school-only rules
  are excluded. A blocked collection or a missing published personnel rule leaves a dash.
