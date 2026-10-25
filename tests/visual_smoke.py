#!/usr/bin/env python3
"""Browser smoke tests for the 48 DevOps Academy lesson visualizations."""
from __future__ import annotations

import functools
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "test-results" / "visuals"
WIDTHS = (390, 768, 1440)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    passed, failures = 0, []

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            for width in WIDTHS:
                context = browser.new_context(
                    viewport={"width": width, "height": 860},
                    device_scale_factor=1,
                )
                # Third-party fonts are optional; tests must be deterministic offline.
                context.route("https://fonts.googleapis.com/**", lambda route: route.abort())
                context.route("https://fonts.gstatic.com/**", lambda route: route.abort())

                for number in range(1, 49):
                    lesson = f"{number:02d}"
                    page = context.new_page()
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.on("console", lambda message: (
                        errors.append(message.text)
                        if message.type == "error" and "[DEVOPS ACADEMY]" in message.text
                        else None
                    ))
                    try:
                        response = page.goto(
                            f"{origin}/lessons/{lesson}.html",
                            wait_until="domcontentloaded",
                            timeout=20000,
                        )
                        assert response is not None and response.status == 200, "HTML not served"
                        page.locator("#visual-guide").wait_for(state="visible", timeout=10000)
                        metrics = page.evaluate("""() => ({
                            tables: document.querySelectorAll("#visual-guide .vs-table").length,
                            figures: document.querySelectorAll("#visual-guide figure").length,
                            nodes: document.querySelectorAll("#visual-guide .vs-nodes li").length,
                            decisions: document.querySelectorAll("#visual-guide .vs-steps > li").length,
                            navigation: !!document.querySelector('.sidebar a[href="#visual-guide"]'),
                            overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
                        })""")
                        assert metrics["tables"] == 2, f"tables: {metrics}"
                        assert metrics["figures"] == 2, f"figures: {metrics}"
                        assert metrics["nodes"] == 4, f"nodes: {metrics}"
                        assert metrics["decisions"] == 3, f"decision nodes: {metrics}"
                        assert metrics["navigation"], f"missing navigation link: {metrics}"
                        assert metrics["overflow"] <= 1, f"page horizontally overflows: {metrics}"
                        assert not errors, f"JavaScript errors: {errors}"

                        if lesson in ("06", "20", "44") and width in (390, 1440):
                            # Hide sticky navigation only while capturing the isolated diagram.
                            page.add_style_tag(content=".top{position:static!important}")
                            page.locator("#visual-guide").screenshot(
                                path=str(RESULTS / f"lesson-{lesson}-{width}.png")
                            )
                        passed += 1
                    except Exception as exc:
                        failures.append({"lesson": lesson, "width": width, "error": str(exc)})
                        page.screenshot(
                            path=str(RESULTS / f"failed-{lesson}-{width}.png"),
                            full_page=True,
                        )
                    finally:
                        page.close()
                context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()

    summary = {
        "passed": passed,
        "failed": len(failures),
        "total": passed + len(failures),
        "failures": failures,
    }
    (RESULTS / "report.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"DevOps Academy visual browser checks: {passed}/{passed + len(failures)}")
    for item in failures:
        print(f"FAIL {item['lesson']} ({item['width']}px): {item['error']}")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
