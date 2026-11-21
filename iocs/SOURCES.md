# IOC sources and reproducibility

| Source | URL | Type / contribution | retrieved_date | Reliability tier |
|---|---|---|---|---|
| FBI notice, dated 2026-10-31 | https://www.fbi.gov/investigate/cyber/alerts/2026/north-korea-responsible-for-6-billion-binance-attack | Wallet addresses and attribution | 2026-11-21 | Primary |
| Binance preliminary report | https://www.binance.com/en/square/post/384314395829022 | Described behaviors | 2026-11-21 | Primary |
| Joint advisory AA22-108A | https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-108a | Historical tradecraft context only | Not retrieved (403 on earlier attempt) | Supporting |

The supplied FBI copy was received on 2026-11-17. On 2026-11-21, the official
page's complete address section was extracted through the web retrieval tool
into `raw/fbi_wallets_web_snapshot.txt`. All 628 entries match the supplied copy
exactly, including capitalization and multiplicity: 608 ETH, 19 BTC, 1 SOL.
These are independently counted entries, not a claimed total printed by the FBI.
Direct shell downloading encountered a web challenge; the snapshot is extracted
page text, not original HTML. The notice is on FBI.gov, not an invented IC3 PSA URL.

`raw/sources.json` pins reviewed dates and SHA-256 input hashes. Hashes cover UTF-8
text with LF newlines and no BOM, so Git's Windows line-ending conversion does
not invalidate them. The builder is offline; repeat builds retain retrieval
dates rather than pretending to fetch sources each day. Source updates require
reviewing both inputs and recording their actual new retrieval date and hashes.

## Verification semantics

- FBI `verified=true`: value reconciled to the retrieved official address list.
  This does not validate checksums, current balances, or wallet ownership.
- Behavioral `verified=false`: medium-confidence prose-derived artifacts,
  explicitly separated from published atomic indicators and excluded from the
  wallet lookup. They are detection hypotheses, not proof of compromise.
- Unknown address formats remain in the master with low confidence and are
  excluded from the active wallet lookup; no characters are repaired.
- Only valid EVM formats are lowercased. Bitcoin, Tron, and Solana values retain
  their exact spelling. Chain classification is heuristic; an EVM address alone
  cannot identify a particular EVM network. Checksums are not implemented.

## Optional OTX input

No OTX pulse was supplied, so no OTX indicators or lookup are included.
If supplied later, use UTF-8 CSV with `indicator,type` headers. Other export
schemas require explicit mapping; the script fails rather than guessing.
Add `otx_pulse` metadata to `raw/sources.json`: name, exact pulse HTTPS URL,
retrieved_date, and canonical-text SHA-256. Never substitute a generic OTX URL.
All OTX rows retain low confidence; only wallet values also present in the
reconciled FBI input receive `verified=true`, with explicit corroboration.
Separate source observations are retained when the same value occurs in FBI
and OTX; duplicates within a source are collapsed and reported.

## Rebuild

```bash
make iocs
python3 -m unittest discover -s tests -p 'test_build_iocs.py' -v
```

Outputs: `iocs.csv` and the app's `lookups/binance_ioc_wallets.csv`.
Lookup configuration and case-sensitive matching are implemented in Phase 3.
