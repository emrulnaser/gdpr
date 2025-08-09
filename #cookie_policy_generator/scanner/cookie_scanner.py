from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def extract_cookies_from_url(url):
    options = Options()
    options.add_argument("--headless")        # Run Chrome in headless mode (no UI)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # Useful for some Linux envs

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
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
