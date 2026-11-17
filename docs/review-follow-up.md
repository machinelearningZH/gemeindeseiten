# Review implementation, 17 November 2026

Source: Codex chat “Review and improve Gemeinde pages”, 17 November 2026.
This records dispositions for the existing review rather than a new audit.

| Review item | Disposition |
| --- | --- |
| Priority 1: municipality search with umlauts and transliterations | Implemented in `web/site.js`; regression checks cover Wädenswil, Waedenswil and Wadenswil. |
| Priority 2: political, primary, secondary and combined school filters | Implemented with labelled controls, combined search and result counts. |
| Priority 3: report an error or suggest a link without GitHub | Per-entry email links prefill the name and both URLs; general suggestion link and contact also provided. |
| Priority 4: separate automated and manual review dates | Historical dates shown separately; generated builds never claim a fresh review. Weekly reports carry their own timestamps. |
| Priority 5: purpose and named maintainer | Page and README identify the audience, experimental status, authoritative originals and Team Data contact. |
| CSV as authoritative source | `build-site` validates and generates all entries; duplicate Markdown tables removed. Generation tests check the public output and original links. |
| Weekly HTTP reports with blocked/new/persistent failures | Weekly/manual Actions workflow produces dated JSON and Markdown, compares prior reports, and never removes links. Report tests cover classification, missing history, redaction and file protection. |
| Accessible link names, keyboard focus and mobile names | Named law and feedback links, row/column headers, focus styles, responsive layout, live counts and no-JavaScript fallback implemented. |
| Keep GitHub Pages | Existing Pages deployment actions retained; only static generated files uploaded, using relative asset paths. |
| School coverage mapping and document-title pilot/search | Deferred pending curated relationships, selected pilot data and evidence of staff needs; decisions tracked in `PLAN.md`. |
| Observe five to eight staff completing real tasks | Requires participants; tracked in `PLAN.md`. |

Validation: `make check` passed (44 pytest tests, Node search/filter checks, Ruff lint
and formatting). Workflow YAML, full action SHAs and shell syntax were checked.
The local browser confirmed search, combined filtering, empty/reset states and
desktop/mobile rendering, including table semantics and no horizontal overflow.
Live municipal destinations, hosted Actions and a full accessibility audit were not checked.
