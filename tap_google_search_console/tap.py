"""google-search-console tap class."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import TYPE_CHECKING

from google.auth import exceptions
from google.oauth2 import credentials, service_account
from googleapiclient.discovery import build
from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_google_search_console import streams

if TYPE_CHECKING:
    from google.auth.transport import Request, Response

SCOPES = [
    "https://www.googleapis.com/auth/webmasters",
    "https://www.googleapis.com/auth/webmasters.readonly",
]

API_SERVICE_NAME = "searchconsole"
API_VERSION = "v1"

class ProxyOAuthCredentials(credentials.Credentials):
    def __init__(
        self,
        token: str | None,
        refresh_token: str | None,
        refresh_proxy_url: str | None,
        refresh_proxy_url_auth: str | None,
    ):
        def refresh_handler(request: Request, scopes):
            if not refresh_proxy_url or not refresh_token:
                msg = "Insufficient config for proxy token refresh - 'refresh_proxy_url' and 'refresh_token' required"
                raise ValueError(msg)

            response: Response = request(
                refresh_proxy_url,
                method="POST",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": refresh_proxy_url_auth,
                },
                body=json.dumps(
                    {
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                    }
                ),
            )

            if response.status != HTTPStatus.OK:
                raise exceptions.RefreshError(response.data)

            data: dict = json.loads(response.data)
            access_token = data["access_token"]
            expiry = datetime.now() + timedelta(seconds=data["expires_in"])

            return access_token, expiry

        super().__init__(token, refresh_handler=refresh_handler)


class TapGoogleSearchConsole(Tap):
    """google-search-console tap class."""

    name = "tap-google-search-console"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "oauth_credentials",
            th.ObjectType(
                th.Property(
                    "refresh_proxy_url",
                    th.StringType,
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
                th.Property(
                    "access_token",
                    th.StringType,
                    secret=True,
                    title="Access Token",
                    description="Google OAuth2 access token",
                ),
                th.Property(
                    "refresh_token",
                    th.StringType,
                    secret=True,
                    title="Refresh Token",
                    description="Google OAuth2 refresh token",
                ),
            ),
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

    def _get_credentials(self) -> credentials.Credentials:
        oauth_credentials: dict | None = self.config.get("oauth_credentials")

        if oauth_credentials:
            return ProxyOAuthCredentials(
                token=oauth_credentials.get("access_token"),
                refresh_token=oauth_credentials.get("refresh_token"),
                refresh_proxy_url=oauth_credentials.get("refresh_proxy_url"),
                refresh_proxy_url_auth=oauth_credentials.get("refresh_proxy_url_auth"),
            )

        client_secrets_raw = self.config["client_secrets"]
        if os.path.isfile(client_secrets_raw):  # noqa: PTH113
            with open(client_secrets_raw) as f:  # noqa: PTH123
                client_secrets = json.load(f)
        else:
            client_secrets = json.loads(client_secrets_raw)

        return service_account.Credentials.from_service_account_info(
            client_secrets,
            scopes=SCOPES,
        )

    def discover_streams(self) -> list[streams.GoogleSearchConsoleStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        service = build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=self._get_credentials(),
            cache_discovery=False,
        )

        return [
            streams.PerformanceReportPage(self, service=service),
            streams.PerformanceReportDate(self, service=service),
            streams.PerformanceReportCountry(self, service=service),
            streams.PerformanceReportQuery(self, service=service),
            streams.PerformanceReportDevice(self, service=service),
            streams.PerformanceReportKeys(self, service=service),
        ]


if __name__ == "__main__":
    TapGoogleSearchConsole.cli()
