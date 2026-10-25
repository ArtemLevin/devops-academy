"""Offline regression tests of read-only lab helpers and synthetic HTTP fixture."""
from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from labs.lesson04.environment import parse_os_release
from labs.lesson05.resources import parse_kib_fields, parse_vmstat
from labs.lesson06.http_lab import local_server, probe, run_demo


class EnvironmentTests(unittest.TestCase):
    def test_os_release_parsing(self):
        x = parse_os_release('NAME="Ubuntu"\nVERSION_ID="24.04"\n#note\n')
        self.assertEqual(x, {'NAME': 'Ubuntu', 'VERSION_ID': '24.04'})


class ResourceTests(unittest.TestCase):
    def test_meminfo_parsing(self):
        fields = parse_kib_fields('MemTotal: 16000 kB\nMemAvailable: 250 kB\nSwapFree: 0 kB\n')
        self.assertEqual(fields['MemAvailable'], 250)
        self.assertEqual(fields['SwapFree'], 0)

    def test_vmstat_counters(self):
        self.assertEqual(parse_vmstat('pswpin 11\npswpout 15\npgfault 200\n'),
                         {'pswpin': 11, 'pswpout': 15})


class HttpLabTests(unittest.TestCase):
    def test_isolated_server_statuses(self):
        with local_server() as port:
            cases = [('/health', 200), ('/dependency', 503), ('/missing', 404)]
            for path, status in cases:
                with self.subTest(path=path):
                    result, _ = probe(f'http://127.0.0.1:{port}{path}')
                    self.assertEqual(result, status)

    def test_demo_verdict(self):
        self.assertEqual(run_demo(), {'/health': 200, '/dependency': 503, '/missing': 404})


if __name__ == '__main__':
    unittest.main()
