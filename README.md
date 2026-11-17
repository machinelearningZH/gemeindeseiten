# Gemeindewebsites und Rechtssammlungen im Kanton Zürich

[Gemeindeverzeichnis öffnen](https://machinelearningzh.github.io/gemeindeseiten/)

Für Mitarbeitende der kantonalen und kommunalen Verwaltung: Websites und
Rechtssammlungen von 160 politischen Gemeinden und 60 selbstständigen Schulgemeinden
schnell finden. Suche mit Umlauten oder Umschreibungen, Filter nach Gemeindetyp und
Rückmeldungen per E-Mail über den Link im Kopfbereich.
Für zunächst 14 politische Gemeinden führen zusätzliche Links direkt zur
Gemeindeordnung und zum Personalrecht. «—» kennzeichnet noch nicht erfasste Links.

**Experimentelle Linksammlung; keine offizielle Publikation. Massgeblich sind die
Originalpublikationen der Gemeinden.** Kontakt und Pflege: Team Data, Amt für
Statistik und Daten Kanton Zürich, [datashop@statistik.zh.ch](mailto:datashop@statistik.zh.ch).

## Daten und Prüfstand

Die CSV-Dateien sind die verbindliche Datenquelle für die automatisch erzeugte Seite:

- [Politische Gemeinden](data/municipalities-canton-zurich.csv): manuell recherchiert
  und zuletzt dokumentiert automatisch geprüft am 23. Oktober 2026.
- [Schulgemeinden](data/school-municipalities-canton-zurich.csv): manuell recherchiert
  und zuletzt dokumentiert automatisch geprüft am 26. Oktober 2026.

Grundlage für die Schulgemeinden ist das
[Gemeindeverzeichnis des Gemeindeamts](https://www.zh.ch/content/dam/zhweb/bilder-dokumente/themen/politik-staat/gemeinden/gemeindeverzeichnis.pdf)
mit Stand vom 1. Juli 2026: 24 Primarschul-, 28 Sekundarschul- und 8 Volksschulgemeinden.
Schulen innerhalb einer politischen Gemeinde sind nicht zusätzlich aufgeführt.
Adressen wurden über das [kantonale Schuladressenverzeichnis](https://www.zh.ch/de/bildung/schulen.html)
und die Websites der Schulen recherchiert.

[Wöchentliche HTTP-Prüfberichte](https://github.com/machinelearningZH/gemeindeseiten/actions/workflows/check-links.yml)
unterscheiden erreichbare Links, blockierte automatische Prüfungen und Prüfbedarf.
Eine erfolgreiche HTTP-Prüfung bestätigt die Erreichbarkeit, nicht den Inhalt.
Sie ersetzt keine manuelle Prüfung und ändert die historischen Recherchetermine nicht.

## Entwicklung und Veröffentlichung

```sh
uv sync --locked
uv run build-site
make check
```

Der Build erzeugt ausschliesslich öffentliche Dateien in `_site/`. HTML, CSS und
JavaScript liegen unter `web/`. Die Seite funktioniert ohne Serveranwendung und
bleibt mit GitHub Pages kompatibel; ohne JavaScript wird die gesamte Liste angezeigt.
Nach dem Merge auf `main` veröffentlicht der Pages-Workflow die erzeugte Seite und
beide CSV-Dateien. Auf dem Feature-Branch wird nichts veröffentlicht.

Details zu Datenpflege, Linkprüfung und Pages-Einstellungen:
[Wartung](docs/maintenance.md). Umsetzung des Reviews und bewusst offene Erweiterungen:
[Review-Nachverfolgung](docs/review-follow-up.md).
