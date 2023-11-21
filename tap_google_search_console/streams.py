"""Stream type classes for tap-google-search-console."""

from __future__ import annotations

import typing as t
from pathlib import Path

from tap_google_search_console.client import GoogleSearchConsoleStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class PerformanceReportPage(GoogleSearchConsoleStream):

    name = "performance_report_page"
    dimensions = [
        "date",
        "page",
        "query"
    ]
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    schema_filepath = SCHEMAS_DIR / (name + '.json')
    

class PerformanceReportDate(GoogleSearchConsoleStream):

    name = "performance_report_date"
    dimensions = [
        "date",
        "query"
    ]
    schema_filepath = SCHEMAS_DIR / (name + '.json')

class PerformanceReportCountry(GoogleSearchConsoleStream):

    name = "performance_report_country"
    dimensions = [
        "date",
        "country",
        "query",
    ]
    schema_filepath = SCHEMAS_DIR / (name + '.json')