import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

chromedriver_autoinstaller.install()  # installs matching chromedriver automatically

def extract_cookies_from_url(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service()  # chromedriver_autoinstaller puts chromedriver in PATH
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(url)
        driver.implicitly_wait(5)
        cookies = driver.get_cookies()
        return [{
            "name": c.get("name"),
            "domain": c.get("domain"),
            "path": c.get("path"),
            "secure": c.get("secure"),
            "httpOnly": c.get("httpOnly"),
            "value": c.get("value")
        } for c in cookies]
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
