"""Build a standalone GitHub Pages directory from the two authoritative CSV files."""

import csv
from html import escape
from pathlib import Path
from shutil import copyfile
from string import Template
from typing import Annotated

import typer
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


app = typer.Typer(add_completion=False, pretty_exceptions_enable=False)
DATA_FILES = ("municipalities-canton-zurich.csv", "school-municipalities-canton-zurich.csv")
SCHOOL_TYPES = {
    "Primarschulgemeinde": "primary",
    "Sekundarschulgemeinde": "secondary",
    "Volksschulgemeinde": "combined",
}


class Municipality(BaseModel):
    """The public fields needed for each directory entry."""

    model_config = ConfigDict(str_strip_whitespace=True)

    gemeinde_name: Annotated[str, Field(min_length=1)]
    gemeinde_website_url: HttpUrl
    erlasse_url: HttpUrl
    gemeindeordnung_url: HttpUrl | None = None
    personalrecht_url: HttpUrl | None = None

    @field_validator("gemeindeordnung_url", "personalrecht_url", mode="before")
    @classmethod
    def empty_document_url(cls, value: object) -> object:
        """Allow blank CSV cells for documents not yet captured."""
        return None if isinstance(value, str) and not value.strip() else value


def render_rows(csv_path: Path, *, schools: bool) -> list[str]:
    """Validate CSV entries and escape their contents for the static HTML table."""
    rows = []
    with csv_path.open(encoding="utf-8", newline="") as file:
        for values in csv.DictReader(file):
            entry = Municipality.model_validate(values)
            name = entry.gemeinde_name
            kind = "political"
            if schools:
                prefix = name.split(" ", 1)[0]
                if prefix not in SCHOOL_TYPES:
                    raise ValueError("Unknown school municipality type.")
                kind = SCHOOL_TYPES[prefix]
            cells = "".join(
                f'<td><a href="{escape(str(url))}" aria-label="{label} {escape(name)}">'
                f"{label}</a></td>"
                if url is not None
                else '<td><span aria-label="Noch nicht erfasst">—</span></td>'
                for label, url in (
                    ("Rechtssammlung", entry.erlasse_url),
                    ("Gemeindeordnung", entry.gemeindeordnung_url),
                    ("Personalrecht", entry.personalrecht_url),
                )
            )
            rows.append(
                f'<tr data-type="{kind}">'
                f'<th scope="row"><a href="{escape(str(entry.gemeinde_website_url))}">'
                f"{escape(name)}</a></th>{cells}</tr>"
            )
    if not rows:
        raise ValueError("Municipality CSV must not be empty.")
    return rows


def build_site(source: Path, output: Path) -> None:
    """Generate only the public HTML, assets and CSV downloads in output."""
    rows = render_rows(source / "data" / DATA_FILES[0], schools=False)
    rows.extend(render_rows(source / "data" / DATA_FILES[1], schools=True))
    html = Template((source / "web" / "index.html").read_text(encoding="utf-8")).substitute(
        rows="\n".join(rows), count=len(rows)
    )
    (output / "data").mkdir(parents=True, exist_ok=True)
    (output / "index.html").write_text(html, encoding="utf-8")
    (output / ".nojekyll").touch()
    for filename in ("site.css", "site.js"):
        copyfile(source / "web" / filename, output / filename)
    for filename in DATA_FILES:
        copyfile(source / "data" / filename, output / "data" / filename)


@app.command()
def main() -> None:
    """Build the directory from data/ and web/ in the current checkout."""
    try:
        build_site(Path.cwd(), Path("_site"))
    except (OSError, ValueError) as error:
        typer.echo(f"Site build failed: {type(error).__name__}.", err=True)
        raise typer.Exit(2) from error
    typer.echo("Built site in _site")


if __name__ == "__main__":
    app()
