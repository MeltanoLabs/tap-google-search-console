# tap-google-search-console

`tap-google-search-console` is a Singer tap for google-search-console.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

Install from GitHub:

```bash
pipx install git+https://github.com/MeltanoLabs/tap-google-search-console@main
```

## Configuration

### Accepted Config Options

#### site_url
Required

The site you want to retrieve metrics for, preceeded with `sc-domain` - i.e. `sc-domain:meltano.com`.
Your client secrets must have permission to access this site.

#### client_secrets
Required

A JSON string of your Google service account client secrets

https://developers.google.com/identity/protocols/oauth2/service-account

#### start_date
Required

The date from which you want to retrive metrics from.

#### include_freshest_data
Default: `True`

Search data for the latest few days can change due to late received data and processing at Google. If you do not want to retrieve that is not 'final', this value can be set to `False`

If this value is set to `False` you will not be able to retrieve data for the most recent dates.

#### backfill_days
Default: 3

The backfill extends the start date by this number. With a start date of 2024-12-01 and a backfill of days. Combining this setting with `include_freshest` will mean you always retrieve the latest data, but overwrite this with 'final' data as this is available.

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-google-search-console --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

You will need to generate a service account credential for your Google Account and authorize this account to access the Google Search Console.

https://developers.google.com/identity/protocols/oauth2/service-account

## Usage

You can easily run `tap-google-search-console` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-google-search-console --version
tap-google-search-console --help
tap-google-search-console --config CONFIG --discover > ./catalog.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-google-search-console` CLI interface directly using `poetry run`:

```bash
poetry run tap-google-search-console --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

<!--
Developer TODO:
Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any "TODO" items listed in
the file.
-->

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-google-search-console
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-google-search-console --version
# OR run a test `elt` pipeline:
meltano elt tap-google-search-console target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
