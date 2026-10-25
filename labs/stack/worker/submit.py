"""Submit one synthetic Celery task; fail loudly on unexpected result."""
from tasks import square

if __name__ == "__main__":
    result = square.delay(7)
    print(f"task_id={result.id}", flush=True)
    actual = result.get(timeout=40)
    print(f"actual={actual}; expected=49", flush=True)
    assert actual == 49, f"unexpected task result: {actual}"
    print("PASS: task executed by worker and result returned", flush=True)
