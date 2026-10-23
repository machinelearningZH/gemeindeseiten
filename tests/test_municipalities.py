import csv
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

import pytest


CSV_PATH = Path(__file__).parent.parent / "data" / "municipalities-canton-zurich.csv"
COLUMNS = ["gebietstyp_code", "gemeinde_code", "gemeinde_name"]
URL_COLUMNS = ["gemeinde_website_url", "erlasse_url"]


@pytest.fixture(scope="module")
def rows() -> list[dict[str, str]]:
    with CSV_PATH.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def test_csv_has_expected_columns() -> None:
    with CSV_PATH.open(encoding="utf-8", newline="") as file:
        assert next(csv.reader(file)) == COLUMNS + URL_COLUMNS


def test_csv_has_no_empty_values(rows: list[dict[str, str]]) -> None:
    assert rows
    assert all(all(value.strip() for value in row.values()) for row in rows)


@pytest.mark.parametrize("column", URL_COLUMNS)
def test_municipality_links_are_valid_https_urls(rows: list[dict[str, str]], column: str) -> None:
    for row in rows:
        url = row[column]
        parsed = urlsplit(url)
        assert parsed.scheme == "https" and parsed.hostname, row["gemeinde_name"]
        assert not any(character.isspace() for character in url), row["gemeinde_name"]


@pytest.mark.parametrize("column", ["gemeinde_code", "gemeinde_name"])
def test_csv_values_are_unique(rows: list[dict[str, str]], column: str) -> None:
    values = [row[column] for row in rows]
    assert len(values) == len(set(values))


def test_csv_codes_are_numeric(rows: list[dict[str, str]]) -> None:
    assert all(row["gebietstyp_code"].isdigit() and row["gemeinde_code"].isdigit() for row in rows)


def test_csv_is_sorted_by_municipality_name(rows: list[dict[str, str]]) -> None:
    names = [
        "".join(
            character
            for character in unicodedata.normalize("NFD", row["gemeinde_name"].casefold())
            if not unicodedata.combining(character)
        )
        for row in rows
    ]
    assert names == sorted(names)


def test_readme_table_matches_csv(rows: list[dict[str, str]]) -> None:
    readme = (CSV_PATH.parent.parent / "README.md").read_text(encoding="utf-8")
    table_rows = [line for line in readme.splitlines() if line.startswith("| [")]
    assert len(table_rows) == len(rows)
    for table_row, row in zip(table_rows, rows, strict=True):
        assert [cell.strip() for cell in table_row.split("|")[1:-1]] == [
            f"[{row['gemeinde_name']}]({row['gemeinde_website_url']})",
            f"[Erlasse]({row['erlasse_url']})",
        ]
