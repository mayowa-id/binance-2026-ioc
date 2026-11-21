# Phase 1 checkpoint — 2026-11-17

Uses the user-created `foundation` branch. Existing MIT license preserved.

Implemented Compose, license and General Terms variables, loopback ports,
named data volume, app bind mount, health check, authenticated API wait script,
Make targets, JSON sourcetypes, five indexes, app metadata, directory placeholders.

Official configuration sources reviewed on 2026-11-17:

- https://github.com/splunk/docker-splunk/blob/develop/docs/SETUP.md
- https://github.com/splunk/docker-splunk/blob/develop/docs/advanced/APP_INSTALL.md

Required variables: `SPLUNK_START_ARGS=--accept-license` and
`SPLUNK_GENERAL_TERMS=--accept-sgt-current-at-splunk-com`.

Runtime acceptance pending: Docker and GNU Make were not found here.
Container health, actual indexes, app visibility, and authenticated management
API readiness have not been demonstrated. No detection tests exist yet.
Later-phase implementation files are absent rather than returning false success.

Before Phase 2, obtain the public FBI wallet list and verify its official source
URL, publication date, and expected count. No wallet indicators were added.
