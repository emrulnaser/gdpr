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
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--no-zygote",
                    "--single-process",
                    "--disable-gpu"
                ]
            )

            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
                )
            )

            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Try clicking cookie consent button
            try:
                page.click("button#accept-cookie, .cookie-consent-accept", timeout=5000)
                time.sleep(3)
            except:
                pass  # no consent button found

            # Extract cookies
            cookies = context.cookies()
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
