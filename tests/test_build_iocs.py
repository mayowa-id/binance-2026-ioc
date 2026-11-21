"""Offline tests; wallet examples come only from the checked-in FBI source."""
import contextlib
import csv
import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_iocs', ROOT / 'scripts/build_iocs.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.raw = self.root / 'iocs/raw'
        shutil.copytree(ROOT / 'iocs/raw', self.raw)
        self.manifest = json.loads((self.raw / 'sources.json').read_text())
        self.values = builder.read_wallets(self.raw / 'fbi_wallets.txt')

    def save_manifest(self):
        (self.raw / 'sources.json').write_text(json.dumps(self.manifest), encoding='utf-8')

    def replace_primary(self, values):
        for filename, key in [('fbi_wallets.txt', 'sha256'),
                              ('fbi_wallets_web_snapshot.txt', 'snapshot_sha256')]:
            path = self.raw / filename
            path.write_text('\n'.join(values) + '\n', encoding='utf-8')
            self.manifest['fbi_wallets'][key] = builder.input_digest(path)
        self.save_manifest()

    def run_build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return builder.build(self.root)

    def read_master(self):
        with (self.root / 'iocs/iocs.csv').open(newline='', encoding='utf-8') as handle:
            return list(csv.DictReader(handle))

    def test_real_input_counts_and_idempotence(self):
        summary = self.run_build()
        self.assertEqual(summary['by_chain'], dict(evm=608, bitcoin=19, solana=1, not_applicable=5))
        self.assertEqual(summary['wallet_lookup_rows'], 628)
        self.assertEqual(summary['total'], 633)
        outputs = [self.root / 'iocs/iocs.csv',
                   self.root / 'splunk_app/binance_ioc_detections/lookups/binance_ioc_wallets.csv']
        before = [path.read_bytes() for path in outputs]
        self.run_build()
        self.assertEqual(before, [path.read_bytes() for path in outputs])
        for row in self.read_master():
            self.assertTrue(all(row[field] for field in builder.FIELDS))
        wallets = [row for row in self.read_master() if row['ioc_type'] == 'wallet']
        self.assertTrue(all(row['verified'] == 'true' for row in wallets))

    def test_case_preservation_and_evm_dedup(self):
        evm = self.values[0]
        sol = self.values[-1]
        self.replace_primary([evm, evm.lower(), sol, sol.lower()])
        summary = self.run_build()
        self.assertEqual(summary['duplicates'], 1)
        values = {row['ioc_value'] for row in self.read_master()}
        self.assertIn(evm.lower(), values)
        self.assertIn(sol, values)
        self.assertIn(sol.lower(), values)  # Case variants are distinct for non-EVM.

    def test_unknown_not_silently_repaired_or_deployed(self):
        self.replace_primary(['INVALID_FORMAT_TEST_SENTINEL'])
        result = self.run_build()
        self.assertEqual(result['unknown_format'], 1)
        self.assertEqual(result['wallet_lookup_rows'], 0)
        self.assertIn('INVALID_FORMAT_TEST_SENTINEL', {r['ioc_value'] for r in self.read_master()})

    def test_missing_input_fails(self):
        (self.raw / 'fbi_wallets.txt').unlink()
        with self.assertRaisesRegex(ValueError, 'Supply'):
            self.run_build()

    def test_unreviewed_input_change_fails(self):
        with (self.raw / 'fbi_wallets.txt').open('a') as handle:
            handle.write('\n# changed\n')
        with self.assertRaisesRegex(ValueError, 'changed'):
            self.run_build()

    def test_reconciliation_fails_even_with_updated_input_hash(self):
        path = self.raw / 'fbi_wallets.txt'
        path.write_text(self.values[0] + '\n', encoding='utf-8')
        self.manifest['fbi_wallets']['sha256'] = builder.input_digest(path)
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, 'differ'):
            self.run_build()

    def test_crlf_does_not_break_provenance_hash(self):
        path = self.raw / 'fbi_wallets.txt'
        path.write_bytes(path.read_text().replace('\n', '\r\n').encode())
        self.assertEqual(self.run_build()['wallet_lookup_rows'], 628)

    def test_otx_requires_provenance(self):
        (self.raw / 'otx_pulse.csv').write_text('indicator,type\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'provenance'):
            self.run_build()

    def test_otx_verification_and_stale_output(self):
        path = self.raw / 'otx_pulse.csv'
        # Test-only provenance points to the supplied source; not a claimed OTX pulse.
        with path.open('w', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(['indicator', 'type'])
            writer.writerow([self.values[0], 'wallet'])
            writer.writerow(['/opt/homebrew/Cellar/pyenv/2.8.0/libexec/pyenv_', 'filepath'])
        self.manifest['otx_pulse'] = dict(name='OTX test fixture',
            url=self.manifest['fbi_wallets']['url'], retrieved_date='2026-11-21',
            sha256=builder.input_digest(path))
        self.save_manifest()
        self.run_build()
        rows = [r for r in self.read_master() if r['category'] == 'supplementary']
        self.assertEqual({r['verified'] for r in rows}, {'true', 'false'})
        self.assertTrue(all(r['confidence'] == 'low' for r in rows))
        optional = self.root / 'splunk_app/binance_ioc_detections/lookups/otx_supplementary_iocs.csv'
        self.assertTrue(optional.exists())
        path.unlink()
        self.run_build()
        self.assertFalse(optional.exists())


if __name__ == '__main__':
    unittest.main()
