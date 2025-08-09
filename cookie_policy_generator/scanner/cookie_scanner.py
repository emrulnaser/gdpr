from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import shutil

def extract_cookies_from_url(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Path to chromium in Render
    chrome_path = shutil.which("chromium-browser")
    driver_path = shutil.which("chromedriver")

    chrome_options.binary_location = chrome_path
    service = Service(driver_path)

    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get(url)
        driver.implicitly_wait(5)  # Wait for page to load JS cookies

        selenium_cookies = driver.get_cookies()
        cookie_list = []
        for c in selenium_cookies:
            cookie_list.append({
                "name": c.get("name"),
                "domain": c.get("domain"),
                "path": c.get("path"),
                "secure": c.get("secure"),
                "httpOnly": c.get("httpOnly"),
                "value": c.get("value")
            })
        return cookie_list
    except Exception as e:
        return [{
            "name": "Error",
            "domain": "N/A",
            "path": "/",
            "secure": False,
            "httpOnly": False,
            "value": str(e)
        }]
    finally:
        driver.quit()
