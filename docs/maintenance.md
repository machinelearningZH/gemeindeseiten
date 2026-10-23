## Links prüfen

```sh
uv run check-links
uv run check-links --help
make check-links
make check-links CONFIG=pfad/config.yaml
```

Prüft beide URL-Spalten der CSV mit HTTPX-GET-Anfragen, folgt Weiterleitungen und gibt für
jeden Link den HTTP-Status oder Verbindungsfehler mit Rich aus. Ergebnisse erscheinen
sofort nach Abschluss der jeweiligen Anfrage mit Fortschrittszähler; Start und
Zusammenfassung zeigen Parallelität, Timeout und Gesamtlaufzeit. Typer stellt Hilfe
und Parameterprüfung bereit. CSV-Pfad, Netzwerk-Timeout, Parallelität und User-Agent
stehen in `config.yaml` (Standard: acht parallele Anfragen, 20 Sekunden Timeout).
Mit `uv run check-links --config pfad/config.yaml` lässt sich eine andere Konfiguration
wählen; relative CSV-Pfade beziehen sich auf deren Verzeichnis.

Exit-Code `0` bedeutet, dass alle Links erreichbar sind; `1` bedeutet, dass mindestens
eine Prüfung fehlgeschlagen ist; `2` meldet ungültige Konfiguration oder Eingabedaten.
Start, jedes Prüfergebnis, Zusammenfassung und Bedienfehler werden zusätzlich als JSON
über `logging` auf stderr protokolliert. Die Ergebnisprotokolle enthalten Gemeinde,
URL-Spalte, Erreichbarkeit und verstrichene Zeit; URLs und rohe Netzwerkfehler stehen
nur in der lesbaren Konsolenausgabe. Bedienfehler enthalten keine Konfigurationswerte
oder CSV-Inhalte.
Die Prüfung erkennt keine inhaltlich falschen Seiten oder defekten JavaScript-Ansichten.
Zugriffssperren (z. B. HTTP 403) werden als fehlgeschlagene Prüfung gemeldet.

Der Python-Code liegt in `src/municipalities/`, die Tests in `tests/`.
Für die Entwicklung: `make sync` installiert deklarierte Abhängigkeiten, `make format`
formatiert den Code und `make check` prüft Linting, Tests und Formatierung.
`make lint` und `make test` führen die Prüfungen einzeln aus; `make` zeigt die Ziele.

## Veröffentlichung

Im neu angelegten Repository unter
[Settings → Pages](https://github.com/machinelearningZH/gemeindeseiten/settings/pages)
die Veröffentlichung erneut aktivieren: unter **Build and deployment → Source**
die Option **GitHub Actions** wählen und die gewünschte Sichtbarkeit festlegen.
Pages-Einstellungen werden bei einer Neuanlage des Repositorys nicht übernommen.
Bei öffentlicher Veröffentlichung lautet die Standardadresse
`https://machinelearningzh.github.io/gemeindeseiten/`; massgeblich ist die in den
Pages-Einstellungen angezeigte Adresse. Der Workflow übernimmt den URL-Pfad automatisch.

Die Workflow-Dateien unter `.github/workflows/` sowie alle benötigten Projektdateien
einschliesslich `uv.lock` müssen mit versioniert und auf `main` vorhanden sein.
Der Workflow **Publish README to GitHub Pages** veröffentlicht diese README bei Änderungen
auf `main` und kann dort auch manuell gestartet werden. Die CSV-Datei wird mit veröffentlicht.

Bei Datenänderungen CSV und Tabelle gemeinsam aktualisieren; die Tests prüfen ihre Übereinstimmung.
