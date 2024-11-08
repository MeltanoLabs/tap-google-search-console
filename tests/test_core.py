# ruff: noqa: E501

"""Tests standard tap features using the built-in SDK tests library."""

import datetime

from singer_sdk.testing import get_tap_test_class

from tap_google_search_console.tap import TapGoogleSearchConsole

SAMPLE_CONFIG = {
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    "site_url": "sc-domain:meltano.com",
    "client_secrets": '{"type": "service_account","project_id": "1234","private_key_id": "1234","private_key": "-----BEGIN PRIVATE KEY-----\\\\n-----END PRIVATE KEY-----\\n","client_email": "me@.iam.gserviceaccount.com","client_id": "123","auth_uri": "https://accounts.google.com/o/oauth2/auth","token_uri": "https://oauth2.googleapis.com/token","auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/something.iam.gserviceaccount.com"}',
}


# Run standard built-in tap tests from the SDK:
TestTapGoogleSearchConsole = get_tap_test_class(
    tap_class=TapGoogleSearchConsole,
    config=SAMPLE_CONFIG,
)
