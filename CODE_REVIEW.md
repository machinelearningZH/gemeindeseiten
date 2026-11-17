# Code review — 17 November 2026

The review identified **1 finding: 0 critical, 0 high, 0 medium, and 1 low**.
Production code and configuration were reviewed without modification. Test and
documentation improvements are coordinated separately by `p-review-all`.

## F001 — Validate User-Agent before constructing the HTTP client

- **Category:** configuration validation / reliability
- **Classification:** confirmed defect
- **Severity:** low
- **Location:** `src/municipalities/check_links.py:37`,
  `src/municipalities/check_links.py:251-255`; downstream handling at
  `.github/workflows/check-links.yml:69-73`.
- **Evidence and trigger:** `Settings.user_agent` rejects empty values and CR/LF,
  but accepts non-ASCII values. A local `CliRunner` invocation with otherwise valid
  CSV/YAML and `user_agent: MunicipalityLinkChecker Zürich` raised
  `UnicodeEncodeError` when HTTPX encoded its headers. No network request was
  needed. The invocation exited **1**, before writing a requested report, rather
  than reporting invalid configuration with the documented exit code **2**.
- **Impact:** a localized operator-supplied header aborts the entire batch instead
  of producing an input error. The weekly workflow deliberately tolerates exit 1
  for unsuccessful HTTP checks; when the other dataset produces reports, its
  artifact can therefore be uploaded successfully while this dataset is absent.
  Both committed configurations currently use valid ASCII values and are
  unaffected.
- **Smallest robust fix:** constrain User-Agent to valid printable ASCII during
  `Settings` validation, preserving the existing empty-value and CR/LF protections.
  Route rejected values through the existing redacted configuration-error path
  before constructing the client or scheduling requests. No dependency or
  workflow redesign is needed. Non-ASCII header values cannot be sent by the
  current HTTPX interface, so rejection does not remove working behavior.
- **Regression evidence:**
  `tests/test_check_links.py:208`,
  `test_invalid_configuration_is_rejected[non_ascii_user_agent]`, now preserves
  the failing exit-code expectation. This exposes existing production behavior;
  the review introduced no production change.

## Coverage

Reviewed both Python entry points and their callers; CSV loading and URL
validation; HTML escaping and public build output; HTTP concurrency, redirects,
errors, report comparison, output-file protection and logging; search/filter
JavaScript and responsive CSS/HTML; maintained tests and documentation; packaging,
operator configuration, Makefile, dependency-update configuration and all three
Actions workflows. CSV data was inspected through existing structural/build tests;
individual external destinations and legal content were not reverified.

## Validation

- Final coordinator check:
  `UV_OFFLINE=1 UV_CACHE_DIR=/tmp/gemeindeseiten-coordinator-review-cache uv run --no-sync ruff check --no-cache .`
  — passed.
- Final coordinator check, with the same environment prefix:
  `uv run --no-sync ruff format --check --no-cache .` — passed (13 files).
- `node tests/test_search.cjs` — passed, including search normalization, combined
  filters, empty state and reset.
- `git diff --check` — passed.
- Local `CliRunner` reproduction of F001 — confirmed `UnicodeEncodeError`, exit 1,
  before network access.
- Offline workflow inspection — all three YAML files parsed, all action references
  use 40-character SHAs, and every shell `run` step passed `bash -n`. This does not
  establish that hosted action revisions or deployments execute successfully.

- Test reviewer:
  `UV_OFFLINE=1 UV_CACHE_DIR=/tmp/gemeindeseiten-review-uv-cache uv run --no-sync pytest -q`
  — baseline **53 passed**; final full suite **62 passed, 1 failed**, using the
  existing CPython 3.15.2 environment.
  The sole failure is the retained F001 regression identified above. Sandbox
  loopback-port restrictions initially caused six fixture errors; the reviewer
  reran with permission for the local HTTP server, so those were environment
  failures rather than production defects.

## Test and documentation improvements

- Strengthened invalid-configuration tests with valid CSV input and a forbidden
  request check. Previously, a missing CSV could make these tests pass even if
  configuration validation accepted an invalid value.
- Added protection checks for report/summary outputs colliding with configuration,
  CSV, previous reports or each other; verified streaming checks close responses
  without reading their bodies; checked invalid/empty school data preserves an
  existing site.
- Documented development prerequisites and the ASCII User-Agent workaround;
  removed obsolete container instructions and tracked the expired certifi
  exception separately. Documentation describes the current behavior without
  claiming that F001 is fixed.

## Limits and follow-up

No external requests, dependency installations, production fixes, commits or
deployments were performed. Hosted Actions/Pages, real browser/assistive-technology
behavior, dependency advisories and the currency of legal documents were not
verified. The CI Python 3.13/3.14 matrix was not rerun locally. No other actionable
code findings were confirmed in the reviewed paths.

The expired certifi cooldown exception is tracked in `PLAN.md`; its removal and
lockfile regeneration were outside this review's configuration-write boundary.
