# Phase 2 checkpoint — 2026-11-21

Branch: `feat/iocs`. No push or merge performed by the agent.

Implemented an offline standard-library IOC builder, input provenance manifest,
retrieved FBI address snapshot, normalized master, generated wallet lookup,
incident summary, source records, and nine pipeline tests. No additional Python
dependencies are needed for normalization.

| Measure | Result |
|---|---:|
| Supplied FBI entries | 628 |
| Exact entries reconciled against official page | 628 |
| EVM wallet rows | 608 |
| Bitcoin wallet rows | 19 |
| Solana wallet rows | 1 |
| Behavioral hypotheses | 5 |
| Master rows | 633 |
| Active wallet lookup rows | 628 |
| Duplicates | 0 |
| Unknown formats | 0 |
| OTX input | Not supplied |

Validation: `make iocs` passed in WSL. Nine offline tests passed on Windows
Python 3.13; repeated builds produced byte-identical CSV output. Provenance
hashing also survives CRLF/LF checkout differences.

Limits: no checksum or on-chain ownership validation; EVM network identity is
not inferred. Behavioral rows are explicitly unverified hypotheses. The older
CISA advisory could not be downloaded (403); no indicators or ATT&CK mappings
were imported from it. No Splunk detection or ingestion checks apply yet.

Next phase, only after review: lookup definitions, deterministic synthetic
events, and ingestion. Preserve case-sensitive non-EVM matching.
