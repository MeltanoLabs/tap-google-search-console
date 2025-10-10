"""Stream type classes for tap-google-search-console."""

from __future__ import annotations

from pathlib import Path

from tap_google_search_console.client import AggType, GoogleSearchConsoleStream

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

class PerformanceReportKeys(GoogleSearchConsoleStream):
    """Stream for raw Google Search Console performance data (preserves 'keys')."""

    name = "performance_report_keys"
    # 'dimensions' isn't used here since we're not unpacking 'keys'
    dimensions = ("date", "query",)
    schema_filepath = SCHEMAS_DIR / (name + ".json")
    agg_type = AggType.byProperty

    def get_records(
        self,
        context: dict[Any, Any] | None,
    ):
        """Yield records with 'date' extracted for replication."""
        for row in self.get_raw_records(context):
            # Extract date from keys if available
            if "keys" in row and isinstance(row["keys"], list) and len(row["keys"]) > 0:
                row["date"] = row["keys"][0]
            else:
                row["date"] = None
            yield row

