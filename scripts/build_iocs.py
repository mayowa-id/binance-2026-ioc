#!/usr/bin/env python3
"""Build offline, deterministic IOC artifacts from explicitly attributed inputs."""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ['ioc_value', 'ioc_type', 'chain', 'category', 'source_name',
          'source_url', 'retrieved_date', 'confidence', 'verified', 'notes']
LOOKUP_FIELDS = ['indicator', 'chain', 'category', 'source', 'confidence']
BASE58 = r'[1-9A-HJ-NP-Za-km-z]'


def input_digest(path):
    # Git may check out text as CRLF on Windows; hash canonical LF text.
    return hashlib.sha256(path.read_text(encoding='utf-8-sig').encode('utf-8')).hexdigest()


BEHAVIORS = [
    ('pyenv replacement sequence', 'endpoint',
     '/opt/homebrew/Cellar/pyenv/2.8.0/libexec/pyenv_'),
    ('install-time execution from interview assignment repository', 'endpoint', ''),
    ('stolen deployment token used to deploy container', 'cloud', ''),
    ('EIP-7702 delegation and nonce manipulation', 'chain', ''),
    ('rapid hot-wallet outflows across chains', 'wallet', ''),
]


def classify_wallet(value):
    """Format heuristics only; no checksum, ownership, or chain-state validation."""
    if re.fullmatch(r'0x[0-9a-fA-F]{40}', value):
        return value.lower(), 'evm'
    if (re.fullmatch(r'[13]' + BASE58 + r'{25,34}', value)
            or re.fullmatch(r'bc1[ac-hj-np-z02-9]{11,71}', value)
            or re.fullmatch(r'BC1[AC-HJ-NP-Z02-9]{11,71}', value)):
        return value, 'bitcoin'
    if re.fullmatch('T' + BASE58 + '{33}', value):
        return value, 'tron'
    if re.fullmatch(BASE58 + '{32,44}', value):
        return value, 'solana'
    return value, 'unknown'


def read_wallets(path):
    values = []
    for number, line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if re.fullmatch(r'(ETH|EVM|Ethereum|BTC|Bitcoin|TRX|Tron|SOL|Solana)( addresses)?:?', line, re.I):
            continue
        if any(char.isspace() for char in line):
            raise ValueError(f'{path}:{number}: expected one address per line; clarify input format')
        values.append(line)
    if not values:
        raise ValueError('FBI input contains no address entries')
    return values


def validate_source(source):
    if not source.get('name') or not source.get('url', '').startswith('https://'):
        raise ValueError('Source needs a name and exact HTTPS URL')
    date.fromisoformat(source['retrieved_date'])


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def build(root):
    raw = root / 'iocs/raw'
    path = raw / 'fbi_wallets.txt'
    if not path.is_file():
        raise ValueError('Supply iocs/raw/fbi_wallets.txt; no placeholder indicators permitted')
    manifest = json.loads((raw / 'sources.json').read_text(encoding='utf-8'))
    fbi, binance = manifest['fbi_wallets'], manifest['binance_report']
    for source in (fbi, binance):
        validate_source(source)
    if input_digest(path) != fbi['sha256']:
        raise ValueError('FBI raw input changed: review provenance and update sources.json before rebuilding')
    snapshot = raw / 'fbi_wallets_web_snapshot.txt'
    if input_digest(snapshot) != fbi['snapshot_sha256']:
        raise ValueError('Official FBI snapshot hash mismatch')
    values = read_wallets(path)
    official_values = read_wallets(snapshot)
    if Counter(values) != Counter(official_values):
        raise ValueError('Supplied FBI entries differ from the retrieved official snapshot')
    rows, seen = [], set()
    duplicates = 0
    for original in values:
        value, chain = classify_wallet(original)
        if value in seen:
            duplicates += 1
            continue
        seen.add(value)
        rows.append(dict(zip(FIELDS, [value, 'wallet', chain, 'theft-associated',
            fbi['name'], fbi['url'], fbi['retrieved_date'],
            'high' if chain != 'unknown' else 'low', 'true',
            'Reconciled with official page snapshot; not checksum or ownership validation. '
            + ('Unrecognized format; excluded from active wallet lookup.' if chain == 'unknown'
               else 'Format heuristic; EVM normalized only.')])))

    supplementary = []
    otx = raw / 'otx_pulse.csv'
    if otx.exists():
        metadata = manifest.get('otx_pulse')
        if not metadata:
            raise ValueError('OTX input requires otx_pulse provenance in sources.json')
        validate_source(metadata)
        if input_digest(otx) != metadata['sha256']:
            raise ValueError('OTX input hash does not match reviewed provenance')
        with otx.open(encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle)
            if not {'indicator', 'type'} <= set(reader.fieldnames or []):
                raise ValueError('OTX CSV requires indicator,type headers; clarify other export formats')
            otx_seen = set()
            for item in reader:
                original, kind = item['indicator'].strip(), item['type'].strip().lower()
                if not original or not kind:
                    raise ValueError('OTX indicator and type must not be blank')
                value, chain = classify_wallet(original)
                if kind in {'wallet', 'address', 'cryptocurrency', 'cryptocurrency address'}:
                    kind = 'wallet'
                else:
                    # Never lowercase non-wallet observables or guess their representation.
                    value, chain = original, 'not_applicable'
                key = kind, value
                if key in otx_seen:
                    duplicates += 1
                    continue
                otx_seen.add(key)
                corroborated = kind == 'wallet' and value in seen
                primary = fbi['url'] if corroborated else ''
                row = dict(zip(FIELDS, [value, kind, chain, 'supplementary',
                    'AlienVault OTX (supplementary)', metadata['url'], metadata['retrieved_date'],
                    'low', 'true' if corroborated else 'false',
                    'Corroborated by supplied FBI file: ' + primary if corroborated
                    else 'Community-unverified; no primary-source corroboration.']))
                rows.append(row)
                supplementary.append(dict(indicator=value, ioc_type=kind, chain=chain,
                    source=metadata['url'], confidence='low', verified=row['verified'],
                    corroboration=primary))

    for description, category, artifact in BEHAVIORS:
        rows.append(dict(zip(FIELDS, [artifact or description, 'behavior', 'not_applicable',
            category, binance['name'], binance['url'], binance['retrieved_date'], 'medium',
            'false', 'Described behavior, not a published atomic IOC or hash: ' + description])))
    rows.sort(key=lambda row: (row['ioc_type'], row['ioc_value'], row['source_name']))
    lookups = root / 'splunk_app/binance_ioc_detections/lookups'
    wallet_rows = [dict(indicator=r['ioc_value'], chain=r['chain'], category=r['category'],
                        source=r['source_url'], confidence=r['confidence'])
                   for r in rows if r['ioc_type'] == 'wallet'
                   and r['source_name'] == fbi['name'] and r['chain'] != 'unknown']
    write_csv(root / 'iocs/iocs.csv', FIELDS, rows)
    write_csv(lookups / 'binance_ioc_wallets.csv', LOOKUP_FIELDS, wallet_rows)
    optional = lookups / 'otx_supplementary_iocs.csv'
    if supplementary:
        write_csv(optional, ['indicator', 'ioc_type', 'chain', 'source', 'confidence',
                            'verified', 'corroboration'], supplementary)
    elif optional.exists():
        optional.unlink()  # Remove stale generated data when an optional input is removed.
    summary = dict(total=len(rows), by_type=dict(Counter(r['ioc_type'] for r in rows)),
        by_chain=dict(Counter(r['chain'] for r in rows)), duplicates=duplicates,
        unknown_format=sum(r['chain'] == 'unknown' for r in rows),
        fbi_input_entries=len(values), wallet_lookup_rows=len(wallet_rows),
        otx_included=bool(supplementary))
    print(json.dumps(summary, indent=2, sort_keys=True))
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        build(args.root)
    except (ValueError, KeyError, OSError, csv.Error) as exc:
        parser.exit(1, f'IOC build failed: {exc}\n')
