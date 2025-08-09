from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shutil
import requests
import traceback
import time

def extract_cookies_from_url(url):
    # Ensure URL starts with http or https
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        # If Chromium or Chromedriver NOT available, fallback to requests
        if shutil.which("chromium-browser") is None or shutil.which("chromedriver") is None:
            resp = requests.get(url, timeout=10, verify=False)
            return [{"name": k, "value": v} for k, v in resp.cookies.get_dict().items()]

        # Setup Selenium with Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Add user-agent string
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        )

        chrome_path = shutil.which("chromium-browser")
        driver_path = shutil.which("chromedriver")

        chrome_options.binary_location = chrome_path
        service = Service(driver_path)

        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            driver.get(url)
            
            wait = WebDriverWait(driver, 20)  # wait up to 20 seconds

            # Try clicking consent button if exists (adjust selector as needed)
            try:
                consent_button = wait.until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "button#accept-cookie, .cookie-consent-accept")
                    )
                )
                consent_button.click()
                time.sleep(3)  # wait a bit for cookies to be set
            except:
                pass  # no consent button found, continue
            
            # After consent (or no consent), get cookies
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
        print("❌ extract_cookies_from_url ERROR:", e)
        print(traceback.format_exc())
        return [{
            "name": "Error",
            "domain": "N/A",
            "path": "/",
            "secure": False,
            "httpOnly": False,
            "value": str(e)
        }]
