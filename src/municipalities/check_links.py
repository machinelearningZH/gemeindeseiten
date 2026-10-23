"""Typer CLI for checking municipal websites and law collections from the CSV."""

import csv
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Annotated
from urllib.parse import urlsplit

import httpx
import typer
import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from rich.console import Console
from rich.text import Text


URL_COLUMNS = ("gemeinde_website_url", "erlasse_url")
app = typer.Typer(add_completion=False, pretty_exceptions_enable=False)
console = Console()
logger = logging.getLogger(__name__)


class Settings(BaseModel):
    """Validated operator settings loaded from YAML."""

    model_config = ConfigDict(extra="forbid")

    csv_path: Path
    timeout: Annotated[float, Field(gt=0, allow_inf_nan=False, strict=True)]
    workers: Annotated[int, Field(gt=0, le=32, strict=True)]
    user_agent: Annotated[str, Field(min_length=1, pattern=r"^[^\r\n]+$")]


class JsonFormatter(logging.Formatter):
    """Format operational errors without including potentially sensitive input values."""

    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "logger": record.name,
                "exception": record.exc_info[0].__name__ if record.exc_info else None,
            }
        )


def load_settings(config_path: Path) -> Settings:
    """Load YAML settings, resolving the CSV path relative to the configuration file."""
    with config_path.open(encoding="utf-8") as file:
        settings = Settings.model_validate(yaml.safe_load(file))
    if not settings.csv_path.is_absolute():
        settings.csv_path = config_path.parent / settings.csv_path
    return settings


def load_links(csv_path: Path) -> list[tuple[str, str, str]]:
    """Read and validate every municipality and URL before making requests."""
    with csv_path.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        required = {"gemeinde_name", *URL_COLUMNS}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("CSV must contain gemeinde_name and both URL columns.")
        links = []
        for row in reader:
            if any(not row.get(column) or not row[column].strip() for column in required):
                raise ValueError(
                    f"CSV row {reader.line_num} has missing municipality or URL values."
                )
            links.extend((row["gemeinde_name"], column, row[column]) for column in URL_COLUMNS)
    if not links:
        raise ValueError("No URLs found.")
    return links


def check_url(url: str, client: httpx.Client) -> tuple[bool, str]:
    """Follow redirects and check HTTP availability without downloading the body."""
    try:
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return False, "Invalid HTTP URL"
        with client.stream("GET", url) as response:
            return response.is_success, f"HTTP {response.status_code}"
    except (httpx.RequestError, httpx.InvalidURL, ValueError) as error:
        return False, f"{type(error).__name__}: {error}"


@app.command()
def main(
    config: Annotated[
        Path,
        typer.Option(
            "--config",
            exists=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="YAML configuration file; relative CSV paths resolve from this file.",
        ),
    ] = Path("config.yaml"),
) -> None:
    """Check both URL columns. Exit 1 for unavailable links or 2 for invalid input."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=logging.WARNING, handlers=[handler])
    logger.setLevel(logging.INFO)
    started = perf_counter()
    try:
        settings = load_settings(config)
        links = load_links(settings.csv_path)
    except (OSError, yaml.YAMLError, ValueError) as error:
        if isinstance(error, ValidationError):
            fields = ", ".join(
                ".".join(map(str, item["loc"])) or "configuration"
                for item in error.errors(include_input=False)
            )
            detail = f"Invalid configuration fields: {fields}."
        elif isinstance(error, yaml.YAMLError):
            detail = "Invalid YAML syntax in configuration."
        elif isinstance(error, UnicodeError):
            detail = "Configuration and CSV must use UTF-8 encoding."
        elif isinstance(error, OSError):
            detail = f"Cannot read configuration or CSV: {error.strerror}."
        else:
            detail = str(error)
        logger.error(detail, exc_info=True)
        console.print(detail, style="red", markup=False)
        raise typer.Exit(2) from error

    logger.info(
        "Starting %d link checks: workers=%d, timeout=%gs",
        len(links),
        settings.workers,
        settings.timeout,
    )
    console.print(
        f"Checking {len(links)} links with {settings.workers} workers "
        f"(timeout {settings.timeout:g}s)",
        markup=False,
    )
    failed = 0
    with (
        console.status("Checking links…"),
        httpx.Client(
            timeout=settings.timeout,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client,
        ThreadPoolExecutor(max_workers=settings.workers) as pool,
    ):
        futures = {
            pool.submit(check_url, url, client): (name, column, url) for name, column, url in links
        }
        for completed, future in enumerate(as_completed(futures), start=1):
            name, column, url = futures[future]
            available, detail = future.result()
            failed += not available
            logger.log(
                logging.INFO if available else logging.WARNING,
                "Completed %d/%d: %s [%s] %s; elapsed=%.2fs",
                completed,
                len(links),
                name,
                column,
                "available" if available else "unavailable",
                perf_counter() - started,
            )
            console.print(
                Text.assemble(
                    (f"[{completed}/{len(links)}] ", "dim"),
                    ("OK" if available else "FAIL", "green" if available else "red"),
                    f" {name} [{column}] {url}: {detail}",
                ),
                soft_wrap=True,
            )

    summary = (
        f"{len(links)} checked, {len(links) - failed} available, {failed} unavailable "
        f"in {perf_counter() - started:.2f}s"
    )
    logger.log(logging.WARNING if failed else logging.INFO, summary)
    console.print(
        summary,
        style="bold red" if failed else "bold green",
    )
    raise typer.Exit(int(failed > 0))


if __name__ == "__main__":
    app()
