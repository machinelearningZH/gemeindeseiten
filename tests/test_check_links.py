import csv
import json
import logging
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Barrier, Event, Thread

import httpx
import pytest
import yaml
from rich.text import Text
from typer.testing import CliRunner

from municipalities import check_links


runner = CliRunner()


@pytest.fixture
def client() -> Iterator[httpx.Client]:
    with httpx.Client(
        timeout=1, follow_redirects=True, headers={"User-Agent": "test-checker"}
    ) as client:
        yield client


@pytest.fixture
def website() -> Iterator[str]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            status = {"/ok": 200, "/redirect": 302, "/missing": 404, "/blocked": 403}[self.path]
            self.send_response(status)
            if status == 302:
                self.send_header("Location", "/ok")
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, format: str, *args: object) -> None:
            pass

    with HTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = Thread(target=server.serve_forever)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}"
        finally:
            server.shutdown()
            thread.join()


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/ok", (True, "HTTP 200")),
        ("/redirect", (True, "HTTP 200")),
        ("/missing", (False, "HTTP 404")),
        ("/blocked", (False, "HTTP 403")),
    ],
)
def test_http_status_and_redirects(
    client: httpx.Client, website: str, path: str, expected: tuple[bool, str]
) -> None:
    assert check_links.check_url(website + path, client) == expected


@pytest.mark.parametrize("url", ["", "not-a-url", "file:///etc/passwd"])
def test_invalid_urls_are_rejected(client: httpx.Client, url: str) -> None:
    assert check_links.check_url(url, client) == (False, "Invalid HTTP URL")


@pytest.mark.parametrize(
    "error", [httpx.ConnectError("DNS lookup failed"), httpx.ReadTimeout("timed out")]
)
def test_connection_errors_are_reported(
    client: httpx.Client, monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    def fail_request(*args: object, **kwargs: object) -> None:
        raise error

    monkeypatch.setattr(client, "stream", fail_request)
    available, detail = check_links.check_url("https://example.com/", client)
    assert not available
    assert str(error) in detail


@pytest.fixture
def config_path(tmp_path: Path) -> Path:
    config = tmp_path / "config.yaml"
    config.write_text(
        yaml.safe_dump(
            {
                "csv_path": "municipalities.csv",
                "timeout": 1,
                "workers": 2,
                "user_agent": "test-checker",
            }
        ),
        encoding="utf-8",
    )
    return config


@pytest.mark.parametrize("laws_path", ["/ok", "/missing"])
def test_cli_checks_both_columns_and_returns_exit_status(
    config_path: Path, website: str, laws_path: str
) -> None:
    with config_path.with_name("municipalities.csv").open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["gemeinde_name", "gemeinde_website_url", "erlasse_url"])
        writer.writerow(["Example [red]", website + "/redirect", website + laws_path])
    result = runner.invoke(check_links.app, ["--config", str(config_path)])
    assert result.exit_code == (0 if laws_path == "/ok" else 1), result.output
    assert "Example [red]" in result.output
    assert "gemeinde_website_url" in result.output and "erlasse_url" in result.output
    assert (
        "2 checked, 2 available, 0 unavailable"
        if laws_path == "/ok"
        else "2 checked, 1 available, 1 unavailable"
    ) in Text.from_ansi(result.output).plain


@pytest.mark.parametrize(
    "content",
    ["", "gemeinde_name,gemeinde_website_url,erlasse_url\n", "wrong,columns\nvalue,value\n"],
)
def test_empty_or_malformed_csv_fails_before_requests(
    config_path: Path, content: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path.with_name("municipalities.csv").write_text(content, encoding="utf-8")
    monkeypatch.setattr(check_links, "check_url", lambda *args: pytest.fail("Unexpected request"))
    result = runner.invoke(check_links.app, ["--config", str(config_path)])
    assert result.exit_code == 2


@pytest.mark.parametrize(
    "invalid",
    [
        {"timeout": 0},
        {"timeout": True},
        {"timeout": float("inf")},
        {"workers": 0},
        {"workers": True},
        {"user_agent": ""},
        {"unknown": 1},
    ],
)
def test_invalid_configuration_is_rejected(config_path: Path, invalid: dict[str, object]) -> None:
    values = yaml.safe_load(config_path.read_text())
    values.update(invalid)
    config_path.write_text(yaml.safe_dump(values), encoding="utf-8")
    result = runner.invoke(check_links.app, ["--config", str(config_path)])
    assert result.exit_code == 2


@pytest.mark.parametrize("content", ["invalid: [yaml", "- not-a-mapping"])
def test_malformed_yaml_is_rejected(config_path: Path, content: str) -> None:
    config_path.write_text(content, encoding="utf-8")
    result = runner.invoke(check_links.app, ["--config", str(config_path)])
    assert result.exit_code == 2


def test_missing_config_is_reported_as_cli_error(tmp_path: Path) -> None:
    result = runner.invoke(check_links.app, ["--config", str(tmp_path / "missing.yaml")])
    assert result.exit_code == 2


def test_cli_help() -> None:
    result = runner.invoke(check_links.app, ["--help"])
    assert result.exit_code == 0
    assert "--config" in Text.from_ansi(result.output).plain


def test_json_logging_includes_context_without_exception_values() -> None:
    record = logging.LogRecord(
        "check_links", logging.ERROR, __file__, 1, "Cannot read CSV", (), None
    )
    data = json.loads(check_links.JsonFormatter().format(record))
    assert data["level"] == "ERROR"
    assert data["message"] == "Cannot read CSV"
    assert data["logger"] == "check_links"
    assert data["timestamp"]
    record.exc_info = (ValueError, ValueError("secret configuration value"), None)
    formatted = check_links.JsonFormatter().format(record)
    assert json.loads(formatted)["exception"] == "ValueError"
    assert "secret configuration value" not in formatted


def test_cli_reports_parallel_results_and_logs(
    config_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    barrier = Barrier(2, timeout=5)
    reported = Event()
    config_path.with_name("municipalities.csv").write_text(
        "gemeinde_name,gemeinde_website_url,erlasse_url\n"
        "Example,https://example.com/,https://example.com/laws\n",
        encoding="utf-8",
    )

    def check(url: str, client: httpx.Client) -> tuple[bool, str]:
        barrier.wait()
        if url == "https://example.com/":
            assert reported.wait(timeout=5), "Completed result was blocked by the first URL"
        return True, "HTTP 200"

    original_print = check_links.console.print

    def print_result(*args: object, **kwargs: object) -> None:
        original_print(*args, **kwargs)
        if any("https://example.com/laws" in str(arg) for arg in args):
            reported.set()

    monkeypatch.setattr(check_links, "check_url", check)
    monkeypatch.setattr(check_links.console, "print", print_result)
    with caplog.at_level(logging.INFO, logger=check_links.__name__):
        result = runner.invoke(check_links.app, ["--config", str(config_path)])
    assert result.exit_code == 0, result.output
    assert "[1/2]" in result.output
    assert "[2/2]" in result.output
    assert "workers=2" in caplog.text
    assert "Completed 1/2" in caplog.text
    assert "Completed 2/2" in caplog.text
    assert "2 checked, 2 available, 0 unavailable" in caplog.text
