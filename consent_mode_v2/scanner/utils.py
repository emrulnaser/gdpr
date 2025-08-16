# consent_mode_v2/scanner/utils.py
import requests

def fetch_page_source(url):
    """Fetch HTML source of a page."""
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"ERROR: {e}"
