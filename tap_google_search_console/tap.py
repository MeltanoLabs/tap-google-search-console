"""google-search-console tap class."""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

from google.oauth2 import service_account
from googleapiclient.discovery import build
from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_google_search_console import streams

if TYPE_CHECKING:
    from googleapiclient.discovery import Resource

SCOPES = [
    "https://www.googleapis.com/auth/webmasters",
    "https://www.googleapis.com/auth/webmasters.readonly",
]

API_SERVICE_NAME = "searchconsole"
API_VERSION = "v1"

REFRESH_TOKEN_PROPERTY = th.Property(
    "refresh_token",
    th.StringType(nullable=False),
    required=True,
    secret=True,
    title="Refresh Token",
    description="Google OAuth2 refresh token",
)

class TapGoogleSearchConsole(Tap):
    """google-search-console tap class."""

    name = "tap-google-search-console"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "oauth_credentials",
            th.OneOf(
                th.ObjectType(
                    th.Property(
                        "client_id",
                        th.StringType(nullable=False),
                        required=True,
                        title="Client ID",
                        description="Google OAuth2 client ID",
                    ),
                    th.Property(
                        "client_secret",
                        th.StringType(nullable=False),
                        required=True,
                        secret=True,
                        title="Client Secret",
                        description="Google OAuth2 client secret",
                    ),
                    REFRESH_TOKEN_PROPERTY,
                ),
                th.ObjectType(
                    th.Property(
                        "refresh_proxy_url",
                        th.StringType(nullable=False),
                        required=True,
                        title="Refresh Proxy URL",
                        description="Proxy URL to support token refresh without a client ID/secret",
                    ),
                    th.Property(
                        "refresh_proxy_url_auth",
                        th.StringType,
                        secret=True,
                        title="Refresh Proxy URL Auth",
                        description="Authorization for proxy URL",
                    ),
                    REFRESH_TOKEN_PROPERTY,
                ),
            ),
            required=True,
        ),
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
            default="2017-01-01",
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
            description="Used to backfill the last N days when using fresh data to ensure corrections are applied",  # noqa: E501
            default=3,
        ),
    ).to_dict()

    def _get_service(self) -> Resource:
        client_secrets_raw = self.config["client_secrets"]
        if os.path.isfile(client_secrets_raw):  # noqa: PTH113
            with open(client_secrets_raw) as f:  # noqa: PTH123
                client_secrets = json.load(f)
        else:
            client_secrets = json.loads(client_secrets_raw)

        credentials = service_account.Credentials.from_service_account_info(
            client_secrets,
            scopes=SCOPES,
        )
        return build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=credentials,
            cache_discovery=False,
        )

    def _custom_initialization(self):  # noqa: ANN202
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
            streams.PerformanceReportDevice(self, service=self.service),
            streams.PerformanceReportKeys(self, service=self.service),
        ]


if __name__ == "__main__":
    TapGoogleSearchConsole.cli()
