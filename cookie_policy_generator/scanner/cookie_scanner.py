from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import shutil
import requests
import traceback

def extract_cookies_from_url(url):
    # Ensure URL starts with http or https
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        # If Chromium is NOT available, use requests fallback
        if shutil.which("chromium-browser") is None:
            resp = requests.get(url, timeout=10, verify=False)  # verify=False fixes SSL issue on Render
            return [{"name": k, "value": v} for k, v in resp.cookies.get_dict().items()]

        # Chromium is available → use Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Paths for Render
        chrome_path = shutil.which("chromium-browser")
        driver_path = shutil.which("chromedriver")

        chrome_options.binary_location = chrome_path
        service = Service(driver_path)

        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            driver.get(url)
            driver.implicitly_wait(5)  # wait for JS cookies

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
        # Print full error in logs
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
