import undetected_chromedriver as uc
from selenium.common.exceptions import WebDriverException

def extract_cookies_from_url(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = uc.Chrome(options=options, version_main=138)
        driver.get(url)
        
        cookies = driver.get_cookies()
        driver.quit()
        
        return [{
            'name': cookie['name'],
            'domain': cookie['domain'],
            'expiry': cookie.get('expiry', 'N/A'),
            'description': '', # Selenium does not provide cookie description
        } for cookie in cookies]

    except WebDriverException as e:
        error_message = f"WebDriverException: {e.msg}"
        print(error_message)
        return [{'name': 'Error', 'domain': 'N/A', 'expiry': 'N/A', 'description': error_message}]
    except Exception as e:
        error_message = str(e)
        print(error_message)
        return [{'name': 'Error', 'domain': 'N/A', 'expiry': 'N/A', 'description': error_message}]
