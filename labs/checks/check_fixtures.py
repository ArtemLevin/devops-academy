"""Offline structural checks; does not pretend to validate Docker/K8s runtime behavior."""
from __future__ import annotations

import ast
import pathlib
import sqlite3

ROOT = pathlib.Path(__file__).resolve().parents[1]


def check_sql_fixture() -> int:
    sql = (ROOT / "stack/postgres/init.sql").read_text(encoding="utf-8")
    conn = sqlite3.connect(":memory:")
    try:
        conn.executescript(sql)
        count = conn.execute("SELECT COUNT(*) FROM demo_events").fetchone()[0]
        assert count == 2, count
        assert conn.execute("SELECT COUNT(DISTINCT event_id) FROM demo_events").fetchone()[0] == count
        return count
    finally:
        conn.close()


def check_celery_code() -> None:
    path = ROOT / "stack/worker/tasks.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "square")
    assert any(isinstance(n, ast.Return) for n in fn.body)
    assert any(isinstance(n, ast.FunctionDef) and n.name == "square" for n in tree.body)
    compile(source, str(path), "exec")
    compile((ROOT / "stack/worker/submit.py").read_text(encoding="utf-8"), "submit.py", "exec")


def check_manifest_text() -> None:
    deployment = (ROOT / "kubernetes/deployment.yaml").read_text(encoding="utf-8")
    service = (ROOT / "kubernetes/service.yaml").read_text(encoding="utf-8")
    compose = (ROOT / "stack/compose.yaml").read_text(encoding="utf-8")
    assert all(key in deployment for key in ("readinessProbe:", "livenessProbe:", "requests:", "limits:", "namespace: academy-synthetic"))
    assert "name: academy-web" in deployment and "app: academy-web" in service
    assert "internal: true" in compose
    assert "condition: service_healthy" in compose
    assert "ports:" not in compose  # do not expose database, broker, or worker on the host


if __name__ == "__main__":
    print(f"SQL fixture: {check_sql_fixture()} unique synthetic rows")
    check_celery_code()
    print("Celery fixture: source parses")
    check_manifest_text()
    print("Manifest guardrails: present (not schema/runtime validation)")
    print("PASS: offline fixture checks")
