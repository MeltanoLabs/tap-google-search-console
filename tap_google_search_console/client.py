"""Custom client handling, including google-search-consoleStream base class."""

# ruff: noqa: ANN002, ANN003, G004

from __future__ import annotations

import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Generator

from singer_sdk.streams import Stream

if TYPE_CHECKING:
    from pathlib import Path

API_SERVICE_NAME = "searchconsole"
API_VERSION = "v1"
NOW = datetime.datetime.now(tz=datetime.timezone.utc).date()

BLOCK_SIZE = 25000


class DataState(Enum):
    """Used to indicate whether all data should be extracted or just finalised data."""

    all = auto()  # noqa: A003
    final = auto()


class AggType(Enum):
    """Used to indicate how data should be aggregated in the API call."""

    byProperty = auto()  # noqa: N815
    byPage = auto()  # noqa: N815
    auto = auto()


class GoogleSearchConsoleStream(Stream):
    """Stream class for google-search-console streams."""

    name: str
    dimensions: tuple[str, ...]
    replication_key = "date"
    agg_type: AggType = AggType.auto

    def __init__(self, *args, **kwargs) -> None:  # noqa: D107
        self.service = kwargs.pop("service")
        super().__init__(*args, **kwargs)
        self._primary_keys = [*self.dimensions, "site_url"]

    @property
    def start_date(self) -> str:
        """Return start date for data."""
        return self.config["start_date"]

    @property
    def end_date(self) -> str:
        """Return end date for data."""
        return self.config.get("end_date", NOW).isoformat()

    @staticmethod
    def get_site_url(full_url: str) -> str:
        """Return"""
        return full_url.partition(":")[-1]

    @property
    def datastate(self) -> str:
        """Return enum corresponding to whether API should include."""
        """freshest data or not."""
        choice = (
            DataState.all
            if self.config.get("include_freshest_data")
            else DataState.final
        )
        return choice.name

    def _get_request_body(self, day: str) -> dict:
        return {
            "startDate": day,
            "endDate": day,
            "dimensions": self.dimensions,
            "rowLimit": BLOCK_SIZE,
            "startRow": 0,
            "aggregationType": self.agg_type.name,
            "dataState": self.datastate,
        }

    def _get_query_dates(self, input_ts: str | None) -> list[str]:
        if not input_ts:
            input_ts = "2024-01-01"

        backfill = self.config["backfill_days"]

        # add in a couple days to cover overlap
        starting_ts = datetime.date.fromisoformat(input_ts) - datetime.timedelta(
            days=backfill,
        )
        delta = datetime.date.fromisoformat(self.end_date) - starting_ts
        return [
            (starting_ts + datetime.timedelta(days=d)).isoformat()
            for d in range(delta.days)
        ]

    def get_records(
        self,
        context: dict[Any, Any] | None,
    ) -> Generator[dict, None, None]:
        """Yields records from the API call."""
        ts = self.get_starting_replication_key_value(context)
        for day in self._get_query_dates(ts):
            body = self._get_request_body(day)
            self.logger.debug(f"Syncing data for {day}")
            step = 0
            while True:
                body["startRow"] = body["startRow"] + (BLOCK_SIZE * step)
                query = self.service.searchanalytics().query(
                    siteUrl=self.config["site_url"],
                    body=body,
                )
                resp = query.execute()

                site_url = self.get_site_url(self.config["site_url"])

                if rows := resp.get("rows"):
                    for row in rows:
                        dim_values = row.pop("keys")
                        for k, v in zip(self.dimensions, dim_values):
                            row[k] = v
                        row["site_url"] = site_url
                        yield row
                    step += 1
                else:
                    break

    @property
    def schema_filepath(self) -> Path | None:
        """Return schema filepath."""
        return super().schema_filepath
