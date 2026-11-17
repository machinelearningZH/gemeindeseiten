import csv
from html.parser import HTMLParser
from pathlib import Path

import pytest

from municipalities.build_site import build_site


ROOT = Path(__file__).parent.parent


class Page(HTMLParser):
    def __init__(self, html: str) -> None:
        super().__init__()
        self.rows: list[dict[str, str | None]] = []
        self.links: list[dict[str, str | None]] = []
        self.feed(html)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "tr" and "data-type" in attributes:
            self.rows.append(attributes)
        if tag == "a":
            self.links.append(attributes)


def test_build_publishes_every_csv_entry_and_only_public_files(tmp_path: Path) -> None:
    build_site(ROOT, tmp_path)
    page = Page((tmp_path / "index.html").read_text(encoding="utf-8"))
    assert len(page.rows) == 220
    assert [row["data-type"] for row in page.rows].count("political") == 160
    assert [row["data-type"] for row in page.rows].count("primary") == 24
    assert [row["data-type"] for row in page.rows].count("secondary") == 28
    assert [row["data-type"] for row in page.rows].count("combined") == 8
    for filename in ["municipalities-canton-zurich.csv", "school-municipalities-canton-zurich.csv"]:
        assert (tmp_path / "data" / filename).read_bytes() == (
            ROOT / "data" / filename
        ).read_bytes()
        with (ROOT / "data" / filename).open(encoding="utf-8", newline="") as file:
            for row in csv.DictReader(file):
                assert any(link.get("href") == row["gemeinde_website_url"] for link in page.links)
                for column, label in [
                    ("erlasse_url", "Rechtssammlung"),
                    ("gemeindeordnung_url", "Gemeindeordnung"),
                    ("personalrecht_url", "Personalrecht"),
                ]:
                    if row.get(column):
                        assert any(
                            link.get("href") == row[column]
                            and link.get("aria-label") == f"{label} {row['gemeinde_name']}"
                            for link in page.links
                        )
    assert {
        path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*") if path.is_file()
    } == {
        "index.html",
        "site.css",
        "site.js",
        ".nojekyll",
        "data/municipalities-canton-zurich.csv",
        "data/school-municipalities-canton-zurich.csv",
    }


@pytest.fixture
def source(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    (source / "web").mkdir(parents=True)
    (source / "data").mkdir()
    (source / "web" / "index.html").write_text(
        "<table>$rows</table><p>$count</p>", encoding="utf-8"
    )
    for filename in ["site.css", "site.js"]:
        (source / "web" / filename).write_text("", encoding="utf-8")
    for filename, name in [
        ("municipalities-canton-zurich.csv", 'A <script> & "B"'),
        ("school-municipalities-canton-zurich.csv", "Primarschulgemeinde Beispiel"),
    ]:
        with (source / "data" / filename).open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["gemeinde_name", "gemeinde_website_url", "erlasse_url"])
            writer.writerow(
                [name, "https://example.com/", "https://example.com/laws?a=1&b=2#chapter"]
            )
    return source


def test_build_escapes_content_without_per_entry_feedback(source: Path, tmp_path: Path) -> None:
    output = tmp_path / "output"
    build_site(source, output)
    html = (output / "index.html").read_text(encoding="utf-8")
    assert "<script>" not in html
    assert "A &lt;script&gt; &amp; &quot;B&quot;" in html
    page = Page(html)
    assert len(page.links) == 4
    assert all(not (link.get("href") or "").startswith("mailto:") for link in page.links)
    assert any(
        link.get("href") == "https://example.com/laws?a=1&b=2#chapter" for link in page.links
    )


def test_general_feedback_link_is_in_header_only(tmp_path: Path) -> None:
    build_site(ROOT, tmp_path)
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    header = Page(html.split("</header>", 1)[0])
    feedback = [
        link
        for link in Page(html).links
        if (link.get("href") or "").startswith("mailto:") and "subject=" in link["href"]
    ]
    assert len(feedback) == 1
    assert feedback[0] in header.links
    assert "Rückmeldung</th>" not in html


def test_build_renders_document_links_and_marks_missing_entries(
    source: Path, tmp_path: Path
) -> None:
    (source / "data" / "municipalities-canton-zurich.csv").write_text(
        "gemeinde_name,gemeinde_website_url,erlasse_url,gemeindeordnung_url,personalrecht_url\n"
        "Example,https://example.com/,https://example.com/laws,"
        "https://example.com/constitution?a=1&b=2,https://example.com/personnel\n",
        encoding="utf-8",
    )
    output = tmp_path / "output"
    build_site(source, output)
    html = (output / "index.html").read_text(encoding="utf-8")
    links = Page(html).links
    assert {
        "href": "https://example.com/constitution?a=1&b=2",
        "aria-label": "Gemeindeordnung Example",
    } in links
    assert {
        "href": "https://example.com/personnel",
        "aria-label": "Personalrecht Example",
    } in links
    assert html.count('<span aria-label="Nicht verifiziert">—</span>') == 2
    assert html.count("<td>") == 6


@pytest.mark.parametrize("column", ["gemeindeordnung_url", "personalrecht_url"])
def test_build_rejects_unsafe_document_urls_before_writing(
    source: Path, tmp_path: Path, column: str
) -> None:
    (source / "data" / "municipalities-canton-zurich.csv").write_text(
        f"gemeinde_name,gemeinde_website_url,erlasse_url,{column}\n"
        "Example,https://example.com/,https://example.com/laws,javascript:alert(1)\n",
        encoding="utf-8",
    )
    output = tmp_path / "output"
    with pytest.raises(ValueError):
        build_site(source, output)
    assert not output.exists()


def test_build_rejects_unsafe_urls_before_writing(source: Path, tmp_path: Path) -> None:
    csv_path = source / "data" / "municipalities-canton-zurich.csv"
    csv_path.write_text(csv_path.read_text().replace("https://example.com/", "javascript:alert(1)"))
    output = tmp_path / "output"
    with pytest.raises(ValueError):
        build_site(source, output)
    assert not output.exists()


@pytest.mark.parametrize(
    ("entry", "message"),
    [
        ("", "Municipality CSV must not be empty"),
        (
            "Unbekannte Schulgemeinde,https://example.com/,https://example.com/laws\n",
            "Unknown school",
        ),
    ],
)
def test_invalid_school_data_preserves_existing_site(
    source: Path, tmp_path: Path, entry: str, message: str
) -> None:
    (source / "data" / "school-municipalities-canton-zurich.csv").write_text(
        "gemeinde_name,gemeinde_website_url,erlasse_url\n" + entry, encoding="utf-8"
    )
    output = tmp_path / "output"
    output.mkdir()
    (output / "index.html").write_text("previous site", encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        build_site(source, output)
    assert (output / "index.html").read_text(encoding="utf-8") == "previous site"
    assert list(output.iterdir()) == [output / "index.html"]
