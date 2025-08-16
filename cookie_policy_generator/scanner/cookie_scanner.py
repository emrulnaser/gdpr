import os
import shutil
import traceback
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_cookies_from_url(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        )

        # Try to find installed binaries
        chrome_path = shutil.which("chromium-browser") or shutil.which("google-chrome")
        driver_path = shutil.which("chromedriver")

        if chrome_path and driver_path:
            chrome_options.binary_location = chrome_path
            service = Service(driver_path)
        else:
            # Fallback to webdriver_manager for local dev if binaries not found
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            driver.get(url)
            wait = WebDriverWait(driver, 20)

            # Try clicking cookie consent button
            try:
                consent_button = wait.until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "button#accept-cookie, .cookie-consent-accept")
                    )
                )
                consent_button.click()
                time.sleep(3)
            except:
                pass  # no consent button found

            selenium_cookies = driver.get_cookies()
            return [{
                "name": c.get("name"),
                "domain": c.get("domain"),
                "path": c.get("path"),
                "secure": c.get("secure"),
                "httpOnly": c.get("httpOnly"),
                "value": c.get("value")
            } for c in selenium_cookies]

        finally:
            driver.quit()

    except Exception as e:
        print("❌ ERROR:", e)
        print(traceback.format_exc())
        return [{
            "name": "Error",
            "domain": "N/A",
            "path": "/",
            "secure": False,
            "httpOnly": False,
            "value": str(e)
        }]
