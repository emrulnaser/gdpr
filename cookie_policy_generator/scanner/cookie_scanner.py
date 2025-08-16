import os
import traceback
import time
from playwright.sync_api import sync_playwright

# Use local Playwright browsers folder
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

def extract_cookies_from_url(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        with sync_playwright() as p:
            # Lightweight Chromium launch
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-gpu",
                    "--single-process",
                    "--disable-dev-shm-usage"
                ]
            )

            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
                )
            )

            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=20000)  # 20s timeout

            # Click cookie consent button if present
            try:
                page.click("button#accept-cookie, .cookie-consent-accept", timeout=3000)
                time.sleep(1)
            except:
                pass

            cookies = context.cookies()

            # Close context & browser immediately to free memory
            context.close()
            browser.close()

            return [{
                "name": c.get("name"),
                "domain": c.get("domain"),
                "path": c.get("path"),
                "secure": c.get("secure"),
                "httpOnly": c.get("httpOnly"),
                "value": c.get("value")
            } for c in cookies]

    except Exception as e:
        safe_error = str(e).encode("utf-8", "replace").decode("utf-8")
        safe_trace = traceback.format_exc().encode("utf-8", "replace").decode("utf-8")
        print("❌ ERROR:", safe_error)
        print(safe_trace)

        return [{
            "name": "Error",
            "domain": "N/A",
            "path": "/",
            "secure": False,
            "httpOnly": False,
            "value": safe_error
        }]
