# Wartung

## Daten und Seite pflegen

Die beiden CSV-Dateien unter `data/` sind die einzige Quelle für die Einträge:

- `municipalities-canton-zurich.csv`: politische Gemeinden mit ihren Codes.
  Die optionalen Spalten `gemeindeordnung_url` und `personalrecht_url` enthalten
  die verifizierten Dokumentlinks der politischen Gemeinden; sonst bleiben sie leer.
  Offizielle Dokumentseiten bevorzugen, direkte PDFs verwenden, wenn die Sammlung
  keine eigene Dokumentseite anbietet. «—» auf der Website bedeutet «kein verifizierter Link».
- `school-municipalities-canton-zurich.csv`: selbstständige Schulgemeinden ohne
  Codes der politischen Gemeinden. Der Namensanfang bestimmt den Typ:
  `Primarschulgemeinde`, `Sekundarschulgemeinde` oder `Volksschulgemeinde`.

Einträge nur in der jeweiligen CSV ändern. `uv run build-site` erzeugt daraus
`_site/index.html`, CSS, JavaScript, beide CSV-Downloads und `.nojekyll`.
Die Tests prüfen, dass alle 220 Einträge und ihre Links im erzeugten Verzeichnis
enthalten sind. Bei einer belegten Bestandsänderung auch die entsprechenden
Bestandserwartungen anpassen.

Die Vorlage und die kleinen Browserdateien liegen unter `web/`. Alle lokalen URLs
sind relativ; die Seite funktioniert unter `/gemeindeseiten/` und unter einem
anderen Pages-Basispfad. Suche und Filter laufen ausschliesslich im Browser;
ohne JavaScript bleibt die vollständige Tabelle zugänglich. Es gibt keine
zusätzlichen Dienste, Schriftanbieter oder Analysedienste.

Die Quellenangaben und manuellen Prüfdaten stehen in `web/index.html`.
Prüfdaten nur nach einer tatsächlichen Prüfung ändern; ein Build ist keine Prüfung.
Wöchentliche HTTP-Berichte führen ihren eigenen UTC-Zeitstempel und aktualisieren
die Angaben auf der Website nicht. Eine blockierte Prüfung belegt keinen defekten Link.
Besonderheiten einzelner Schulseiten sind in [NOTES.md](../NOTES.md) dokumentiert.

Für den Bestand der Schulgemeinden das in der README verlinkte kantonale
Gemeindeverzeichnis verwenden. Das Schuladressenverzeichnis enthält auch Schulen
von Einheitsgemeinden und teilweise frühere Namen und Domains.

«Fehler melden / Link vorschlagen» im Kopfbereich öffnet eine Nachricht an
`datashop@statistik.zh.ch` im Mailprogramm. Gemeinde und betroffenen Link bitte
in der Nachricht ergänzen. Es wird nichts automatisch versendet.
Kontakt und Pflege werden in der Seitenvorlage genannt.

## Links prüfen

```sh
uv run check-links
uv run check-links --help
make check-links
make check-links CONFIG=pfad/config.yaml
uv run check-links --config config.schulgemeinden.yaml
```

Der Checker prüft Homepage, Rechtssammlung und alle ausgefüllten optionalen
Dokument-URL-Spalten mit HTTPX-GET-Anfragen, folgt Weiterleitungen
und lädt die Antwortinhalte nicht herunter. Ergebnisse erscheinen nach Abschluss
der jeweiligen Anfrage; die Zusammenfassung nennt Parallelität, Timeout und
Laufzeit. CSV-Pfad, Timeout, Parallelität und User-Agent stehen in `config.yaml`
(Standard: acht parallele Anfragen, 20 Sekunden Timeout). Relative CSV-Pfade
beziehen sich auf das Verzeichnis der Konfiguration. Der User-Agent muss aus
druckbaren ASCII-Zeichen bestehen; andere Werte werden als Eingabefehler abgewiesen.

Exit-Code `0`: alle Links erreichbar; `1`: mindestens eine Prüfung fehlgeschlagen,
auch bei HTTP 403 oder 429; `2`: ungültige Eingabe oder nicht schreibbarer Bericht.
Die Prüfung erkennt keine inhaltlich falschen Seiten oder defekten JavaScript-Ansichten.

Für einen gespeicherten Bericht zuerst das Zielverzeichnis anlegen:

```sh
mkdir -p reports
uv run check-links --report reports/political.json --summary reports/political.md
uv run check-links --config config.schulgemeinden.yaml \
  --report reports/schools.json --summary reports/schools.md
```

Mit `--previous-report pfad/vorher.json` lassen sich aufeinanderfolgende Prüfungen
vergleichen. JSON enthält `checked_at` und pro URL den Status:

| Status | Bedeutung |
| --- | --- |
| `reachable` | HTTP-Anfrage erfolgreich |
| `blocked` | Automatische Prüfung mit HTTP 403 oder 429 blockiert |
| `needs_review` | Anderer HTTP-Fehler, Verbindungsfehler oder ungültige URL |

Fehler werden anhand von URL und URL-Spalte als `new` oder `persistent` eingeordnet.
Ohne vorherigen Bericht lautet die Einordnung `uncompared`; erstmals beobachtet ist
nicht dasselbe wie neu aufgetreten. JSON und Markdown enthalten bei Netzwerkfehlern
nur die Fehlerklasse. URLs sind öffentliche Quelldaten; rohe Netzwerkfehler stehen
nur in der lesbaren Konsolenausgabe. JSON-Logs auf stderr enthalten keine URLs,
rohen Netzwerkfehler, Konfigurationswerte oder CSV-Inhalte bei Bedienfehlern.

Der Workflow **Weekly link report** prüft beide Dateien montags um 07:00 UTC und
kann manuell gestartet werden. Er lädt den Bericht des letzten erfolgreichen Laufs
auf dem Standardbranch zum Vergleich; fehlt er oder ist der Download nicht möglich,
steht dies in der Zusammenfassung. JSON und Markdown sind für 90 Tage als Artefakt
`link-check-reports` verfügbar; die Fehlerübersicht steht direkt in der
[Laufzusammenfassung](https://github.com/machinelearningZH/gemeindeseiten/actions/workflows/check-links.yml).
HTTP-Fehler verhindern die Berichtablage nicht; Eingabe- und Schreibfehler lassen
den Workflow fehlschlagen. Der Workflow ändert weder CSV noch Website und benötigt
nur Lesezugriff auf Repository und frühere Actions-Artefakte.

## Entwicklung und Veröffentlichung

```sh
uv sync --locked
make build-site
make check
```

`make check` führt Ruff, pytest sowie die JavaScript-Selbstprüfung aus und benötigt
für Letztere Node.js. Es werden keine npm-Pakete benötigt. Die lokalen HTTP-Tests
benötigen Zugriff auf einen Loopback-Port. Die CI prüft Python 3.13 und 3.14.

Unter **Settings → Pages → Build and deployment → Source** muss **GitHub Actions**
eingestellt sein. Die [GitHub-Dokumentation zur Veröffentlichungsquelle](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-with-a-custom-github-actions-workflow)
beschreibt die Einstellung und die erforderlichen Repository-Berechtigungen.
Die vorhandene Sichtbarkeit beibehalten. Die veröffentlichte Standardadresse ist
`https://machinelearningzh.github.io/gemeindeseiten/`.

Der [Pages-Workflow](../.github/workflows/pages.yml) baut und veröffentlicht bei
Änderungen auf `main` an `data/**`, `web/**`, `src/municipalities/build_site.py`,
`pyproject.toml`, `uv.lock` oder am Workflow selbst. Er lässt sich auf `main` auch
über **Actions → Publish directory to GitHub Pages → Run workflow** starten.
Änderungen nur an Markdown-Dokumentation und Pushes auf Feature-Branches lösen
keine Veröffentlichung aus.

Der Workflow installiert das Projekt mit `uv sync --locked --no-dev`, führt
`uv run --no-sync build-site` aus und veröffentlicht `_site/` als Pages-Artefakt.
Es enthält HTML, CSS, JavaScript, beide CSV-Dateien und `.nojekyll`.
Die erzeugten Dateien werden nicht eingecheckt. Die CI läuft separat; vor dem
Merge `make check` ausführen.
