"""Custom client handling, including google-search-consoleStream base class."""

from __future__ import annotations
from pathlib import Path
from datetime import date, timedelta

from singer_sdk.streams import Stream


API_SERVICE_NAME = 'searchconsole'
API_VERSION = 'v1'
NOW = date.today()

BLOCK_SIZE = 25000


class GoogleSearchConsoleStream(Stream):
    """Stream class for google-search-console streams."""
    name: str
    dimensions: list[str]
    replication_key = 'date'  # noqa: ERA001

    def __init__(self, *args, **kwargs) -> None:
        self.service = kwargs.pop("service")
        super().__init__(*args, **kwargs)
        self._primary_keys = self.dimensions + ['site_url']

    # @property
    # def _get_schema_filepath(self) -> Path:
    #     return SCHEMAS_DIR / (self.name + '.json')  # noqa: ERA001

    @property
    def start_date(self) -> str:
        return self.config['start_date']
    
    @property
    def end_date(self) -> str:
        return self.config.get('end_date', NOW).isoformat()
    
    @staticmethod
    def get_site_url(full_url: str) -> str:
        """
        Return 
        """
        return full_url.partition(':')[-1]

    def _get_request_body(self, day: str) -> dict:
        return {
            "startDate": day,
            "endDate": day,
            "dimensions": self.dimensions,
            "rowLimit": BLOCK_SIZE,
            "startRow": 0,
        }
    
    def _get_query_dates(self, starting_ts: str) -> List[str]:


        # add in a couple days to cover overlap
        starting_ts = date.fromisoformat(starting_ts) - timedelta(days=2)
        delta = date.fromisoformat(self.end_date) - starting_ts
        return [
            (starting_ts + timedelta(days=d)).isoformat()
            for d in range(delta.days)
        ]

    def get_records(self, context):
        ts = self.get_starting_replication_key_value(context)
        for day in self._get_query_dates(ts):
            body=self._get_request_body(day)
            self.logger.debug(f'Syncing data for {day}')
            step = 0
            while True:
                body['startRow'] = body['startRow'] + (BLOCK_SIZE*step)
                query = self.service.searchanalytics().query(
                    siteUrl=self.config['site_url'],
                    body = body
                )
                resp = query.execute()

                site_url = self.get_site_url(self.config['site_url'])

                if rows:= resp.get('rows'):
                    for row in rows:
                        dim_values = row.pop('keys')
                        for k,v in zip(self.dimensions, dim_values):
                            row[k] = v
                        row['site_url'] = site_url
                        yield row
                    step += 1
                else:
                    break

    @property
    def schema_filepath(self) -> Path | None:
        return super().schema_filepath