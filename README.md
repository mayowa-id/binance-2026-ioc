# Binance public IOC detection lab

A defensive Splunk portfolio project based on public indicators and documented
behaviors from the October 2026 Binance incident. **Phase 1 foundation only:**
no indicators, detection rules, fixtures, or detection test results exist yet.

## Setup

Requires Docker with Linux containers, Compose v2 supporting `up --wait`, Bash,
GNU Make, and Python 3. On Windows use WSL with Docker Desktop integration.
Run from the repository root:

```bash
cp .env.example .env
# Edit .env and replace the example password.
make up
```

Starting the container accepts Splunk's license and current General Terms.
Open http://localhost:8000 (or your configured web port), log in as `admin`,
and find **Binance IOC Detections** under Apps. The management API uses
https://localhost:8089 with a self-signed lab certificate. Ports bind to loopback.

Phase 1 runtime checks:

```bash
docker compose ps
docker compose exec -T splunk /opt/splunk/bin/splunk btool indexes list --app=binance_ioc_detections
docker compose exec -T splunk /opt/splunk/bin/splunk btool props list --app=binance_ioc_detections
```

Confirm container health, app visibility, and indexes `endpoint`, `network`,
`wallet_tx`, `cloud_audit`, `chain_tx` under Settings > Indexes. `btool` shows
configuration; it alone does not prove runtime provisioning.

`make down` preserves indexed data in a named volume. The requested `latest`
image tag is mutable; record the version/digest when validating the runtime.

## Phase checkpoints

1. Foundation (current): runtime acceptance pending.
2. Source verification and IOC normalization.
3. Lookups, deterministic fixtures, and ingestion.
4. Documented detection rules and scheduled searches.
5. Splunk integration tests and generated results matrix.
6. Dashboard and final documentation.

Make targets `iocs`, `testdata`, `load`, `test`, and `all` are wired for later
phases and will fail until their implementation files exist. Do not run
`make all` as a Phase 1 check.

Before Phase 2 normalization, supply `iocs/raw/fbi_wallets.txt`; optionally
supply `iocs/raw/otx_pulse.csv` with its source URL. No indicators will be invented.
Raw files are intended to be committed public inputs; inspect them before
adding data. Credentials belong only in the ignored `.env`.

## Source starting points

- [Binance preliminary report](https://www.binance.com/en/square/post/384314395829022)
- [FBI alert found in initial research](https://www.fbi.gov/investigate/cyber/alerts/2026/north-korea-responsible-for-6-billion-binance-attack)
- [Official Docker-Splunk setup](https://github.com/splunk/docker-splunk/blob/develop/docs/SETUP.md)
- [Official app bind-mount instructions](https://github.com/splunk/docker-splunk/blob/develop/docs/advanced/APP_INSTALL.md)

Reviewed on 2026-11-17. Full incident verification and IOC provenance belong to
Phase 2; the FBI link is not yet a verified wallet-list source.

MIT license; see [LICENSE](LICENSE). For authorized defensive use.
