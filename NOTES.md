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
