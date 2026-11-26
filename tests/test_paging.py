"""Tests the paging of Search Analytics rows."""

from __future__ import annotations

from types import SimpleNamespace

from tap_google_search_console.client import BLOCK_SIZE
from tap_google_search_console.streams import PerformanceReportQuery
from tap_google_search_console.tap import TapGoogleSearchConsole


class _SearchAnalytics:
    """A stub of the Search Analytics API that returns `rows` for one day."""

    def __init__(self, day: str, rows: list[list[str]]) -> None:
        self.day = day
        self.rows = rows

    def searchanalytics(self) -> _SearchAnalytics:
        return self

    def query(self, *, body: dict, **_: str) -> SimpleNamespace:
        rows = self.rows if body["startDate"] == self.day else []
        page = rows[body["startRow"] : body["startRow"] + body["rowLimit"]]
        response = {"rows": [{"keys": list(keys), "clicks": 1} for keys in page]}
        return SimpleNamespace(execute=lambda: response if page else {})


def test_reads_every_page_of_a_day() -> None:
    """A day with more rows than three pages hold yields every row once."""
    rows = [["2024-01-01", f"query {i}"] for i in range(3 * BLOCK_SIZE + 1)]
    tap = TapGoogleSearchConsole(
        config={
            "site_url": "sc-domain:example.com",
            "oauth_credentials": {"access_token": "token"},
        },
    )
    stream = PerformanceReportQuery(tap, service=_SearchAnalytics("2024-01-01", rows))

    queries = [record["query"] for record in stream.get_records(None)]

    assert sorted(queries) == sorted(query for _, query in rows)  # noqa: S101
