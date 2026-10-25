"""Fast offline checks for training fixtures; does not require Docker or Kubernetes."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from labs.checks.check_fixtures import check_sql_fixture, check_celery_code, check_manifest_text


class AdvancedFixtureTests(unittest.TestCase):
    def test_synthetic_postgres_seed(self):
        self.assertEqual(check_sql_fixture(), 2)

    def test_worker_code_parses(self):
        check_celery_code()

    def test_manifest_guardrails(self):
        check_manifest_text()


if __name__ == "__main__":
    unittest.main()
