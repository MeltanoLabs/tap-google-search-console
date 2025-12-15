"""Stream type classes for tap-google-search-console."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Generator

from tap_google_search_console.client import AggType, GoogleSearchConsoleStream

if TYPE_CHECKING:
    from singer_sdk.helpers.types import Context

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class PerformanceReportQuery(GoogleSearchConsoleStream):
    """Class for Performance Report Query."""

    name = "performance_report_query"
    dimensions = (
        "date",
        "query",
    )
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    schema_filepath = SCHEMAS_DIR / (name + ".json")
    agg_type = AggType.byProperty


class PerformanceReportPage(GoogleSearchConsoleStream):
    """Class for Performance Report Query by Page."""

    name = "performance_report_page"
    dimensions = (
        "date",
        "page",
    )
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    schema_filepath = SCHEMAS_DIR / (name + ".json")
    agg_type = AggType.byPage


class PerformanceReportDate(GoogleSearchConsoleStream):
    """Class for Performance Report By Date."""

    name = "performance_report_date"
    dimensions = ("date",)
    schema_filepath = SCHEMAS_DIR / (name + ".json")
    agg_type = AggType.byProperty


class PerformanceReportCountry(GoogleSearchConsoleStream):
    """Class for Performance Report by Country."""

    name = "performance_report_country"
    dimensions = (
        "date",
        "country",
    )
    schema_filepath = SCHEMAS_DIR / (name + ".json")
    agg_type = AggType.byProperty


class PerformanceReportDevice(GoogleSearchConsoleStream):
    """Class for Performance Report by Device."""

    name = "performance_report_device"
    dimensions = (
        "date",
        "device",
    )
    schema_filepath = SCHEMAS_DIR / (name + ".json")
    agg_type = AggType.byProperty


# New stream class that pulls all dimensions from keys
class PerformanceReportKeys(GoogleSearchConsoleStream):
    """Stream for raw Google Search Console performance data (preserves 'keys')."""

    name = "performance_report_keys"
    dimensions = (
        "date",  # Include 'date' for replication key support
        "query",
        "page",
        "country",
        "device",
    )
    schema_filepath = SCHEMAS_DIR / (name + ".json")
    # Use auto aggregation type (byProperty is invalid for multi-dimension)
    agg_type = AggType.auto

    def get_records(
        self,
        context: Context | None,
    ) -> Generator[dict, None, None]:
        """Yield raw API data keeping 'keys' in each row."""
        yield from self.get_raw_records(context)
