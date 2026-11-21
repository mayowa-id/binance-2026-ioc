# Binance public IOC detection lab

A defensive Splunk lab for investigating the October 2026 Binance incident
using public wallet indicators and documented behaviors. Includes 628 sourced
wallet addresses, an IOC normalization pipeline, and a generated Splunk lookup.

## Quick start

Requires Docker with Linux containers, Docker Compose v2, Bash, GNU Make, and
Python 3. On Windows, use WSL with Docker Desktop integration.

```bash
cp .env.example .env
# Replace the example password in .env.
# If port 8000 is occupied, set SPLUNK_WEB_PORT=8001.
make up
make iocs
```

Open http://localhost:8000 (or your configured web port) and log in as `admin`.
The app appears as **Binance IOC Detections**. Starting the container accepts
Splunk's license and current General Terms. Run `make down` to stop the lab
while preserving indexed data.

## IOC pipeline

Raw inputs are stored in `iocs/raw/`. Running `make iocs` generates
`iocs/iocs.csv` and the wallet lookup under
`splunk_app/binance_ioc_detections/lookups/`.

```bash
python3 -m unittest discover -s tests -p 'test_build_iocs.py' -v
```

Wallet indicators are reconciled against an official FBI snapshot. Behavioral
entries are hypotheses derived from Binance's report; they are not confirmed
atomic indicators. Address checksums and ownership are not validated.

See [sources and provenance](iocs/SOURCES.md) and the
[incident summary](docs/incident-summary.md).

For authorized defensive use. [MIT license](LICENSE).
