# Maintenance notes

Routine commands and publication settings: [maintenance guide](docs/maintenance.md).

- Cantonal laws use ZH-Lex's published current-version links
  (`https://www.zhlex.zh.ch/Erlass.html?Open&Ordnr=…`). Keep these rather than
  version-specific detail pages or PDFs, which can point to superseded texts.
- Typer enables styled help on GitHub Actions. CLI text assertions must strip
  ANSI sequences with `Text.from_ansi(...).plain` before matching option names or summaries.
- Retain collection entry pages even when the website opens its first chapter
  (Kleinandelfingen, Nürensdorf and Hombrechtikon).
- Volken uses a municipality-filtered ePublikation link because its municipal
  “Systematische Rechtssammlung” navigation led to a history page during research.
- Check JavaScript and session-based collections in a browser: secondary Dielsdorf,
  primary Höri and secondary Stadel. Stadel uses its download folder as the collection.
  Primary Laufen-Uhwiesen links to SharePoint; secondary Obfelden-Ottenbach links to
  its SharePoint collection from the downloads page.
- Direct PDFs, including Horgen and Wetzikon, may need replacing when new documents
  are published. Kloten and Winterthur use JavaScript-based LexWork pages.
- For ePublikation, verify the publication ID, title, `PUBLISHED` state and publishing
  entity using its public `/api/v1/publications/{id}` record; town names alone also
  match schools. Use the public `#!/search/publications/detail/{id}` link. The HTTP
  checker sees the JavaScript shell, so it cannot detect removal of a hash-routed record.
- Mixed Besoldungsverordnungen qualify as Personalrecht only when the published text
  actually covers municipal staff. Authority-only compensation and school-only rules
  are excluded. A blocked collection or a missing published personnel rule leaves a dash.
