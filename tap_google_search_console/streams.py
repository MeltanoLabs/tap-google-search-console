"""Stream type classes for tap-google-search-console."""

from __future__ import annotations

import typing as t
from pathlib import Path

from tap_google_search_console.client import GoogleSearchConsoleStream, AggType

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")

class PerformanceReportQuery(GoogleSearchConsoleStream):

    name = "performance_report_query"
    dimensions = [
        "date",
        "query"
    ]
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    schema_filepath = SCHEMAS_DIR / (name + '.json')
    agg_type = AggType.byProperty


class PerformanceReportPage(GoogleSearchConsoleStream):

    name = "performance_report_page"
    dimensions = [
        "date",
        "page",
    ]
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    schema_filepath = SCHEMAS_DIR / (name + '.json')
    agg_type = AggType.byPage
    

class PerformanceReportDate(GoogleSearchConsoleStream):

    name = "performance_report_date"
    dimensions = [
        "date",
    ]
    schema_filepath = SCHEMAS_DIR / (name + '.json')
    agg_type = AggType.byProperty

class PerformanceReportCountry(GoogleSearchConsoleStream):

    name = "performance_report_country"
    dimensions = [
        "date",
        "country",
    ]
    schema_filepath = SCHEMAS_DIR / (name + '.json')
    agg_type = AggType.byProperty