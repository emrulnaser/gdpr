import requests
from bs4 import BeautifulSoup

def extract_cookies_from_url(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        scan_url = f"https://2gdpr.com/cookie-scanner?url={url}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
        response = requests.get(scan_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        
        cookies = []
        table = soup.find('table', {'class': 'cookie-scan-report-table'})
        if table:
            rows = table.find_all('tr')
            for row in rows[1:]: # Skip header row
                cols = row.find_all('td')
                if len(cols) >= 6:
                    cookie = {
                        'name': cols[0].text.strip(),
                        'domain': cols[1].text.strip(),
                        'expiry': cols[4].text.strip(),
                        'description': cols[5].text.strip(),
                    }
                    cookies.append(cookie)
        
        return cookies

    except requests.exceptions.RequestException as e:
        return [{'name': 'Error', 'domain': 'N/A', 'expiry': 'N/A', 'description': str(e)}]
    except Exception as e:
        return [{'name': 'Error', 'domain': 'N/A', 'expiry': 'N/A', 'description': 'An unexpected error occurred.'}]
