"""google-search-console tap class."""

from __future__ import annotations
import json

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from google.oauth2 import service_account
from googleapiclient.discovery import build

from tap_google_search_console import streams

SCOPES = [
    'https://www.googleapis.com/auth/webmasters',
    'https://www.googleapis.com/auth/webmasters.readonly',
]

API_SERVICE_NAME = 'searchconsole'
API_VERSION = 'v1'


class TapGoogleSearchConsole(Tap):
    """google-search-console tap class."""

    name = "tap-google-search-console"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "site_url",
            th.StringType,
            required=True,
            description="Project IDs to replicate",
        ),
        th.Property(
            "client_secrets",
            th.StringType,
            description="Google Analytics Client Secrets Dictionary",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
            default='2017-01-01',
        ),
        th.Property(
            "include_freshest_data",
            th.BooleanType,
            description="Include freshest data as detailed here: https://developers.google.com/search/blog/2019/09/search-performance-fresh-data",
            default=True,
        ),
        th.Property(
            "backfill_days",
            th.IntegerType,
            description="Used to backfill the last N days when using fresh data to ensure corrections are applied",
            default=3
        )
    ).to_dict()

    def _get_service(self):
        client_secrets = json.loads(self.config['client_secrets'])
        credentials = service_account.Credentials.from_service_account_info(
            client_secrets,
            scopes=SCOPES
        )
        service = build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=credentials,
            cache_discovery=False
        )
        return service
    
    def _custom_initialization(self):
        self.service = self._get_service()

    def discover_streams(self) -> list[streams.GoogleSearchConsoleStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        self._custom_initialization()
        return [
            streams.PerformanceReportPage(self, service=self.service),
            streams.PerformanceReportDate(self, service=self.service),
            streams.PerformanceReportCountry(self, service=self.service),
            streams.PerformanceReportQuery(self, service=self.service),
        ]


if __name__ == "__main__":
    TapGoogleSearchConsole.cli()
