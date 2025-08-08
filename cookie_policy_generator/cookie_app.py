from flask import Blueprint, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from .scanner.cookie_scanner import extract_cookies_from_url
from .generator.policy_generator import generate_policy

# Blueprint for cookie policy generator
cookie_bp = Blueprint(
    "cookie_bp",
    __name__,
    template_folder="templates"  # Points to: cookie_policy_generator/templates/
)

@cookie_bp.route("/")  # URL: /cookie_policy_generator/
def cookie_policy_tool():
    return render_template("cookie_policy_generator.html")

@cookie_bp.route("/generate-policy", methods=["POST"])
def generate():
    url = request.form["url"]
    cookies = extract_cookies_from_url(url)
    policy = generate_policy(cookies)
    return render_template("cookie_policy_result.html", policy=policy, site=url)

@cookie_bp.route("/lookup-cookie-api", methods=["POST"])
def lookup_cookie_api():
    cookie_name = request.json.get("cookie_name")
    if not cookie_name:
        return jsonify({ "error": "Cookie name is required." }), 400

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        url = f"https://duckduckgo.com/?q=what+is+the+{cookie_name}+cookie&ia=web"
        driver.get(url)
        
        wait = WebDriverWait(driver, 5) # 5 second timeout
        description = None

        # Strategy 1: Look for the Search Assist definition
        try:
            description_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".search-assist-result__description")))
            description = description_element.text
            if description:
                return jsonify({ "description": description })
        except (TimeoutException, NoSuchElementException):
            pass # If it fails, just move to the next strategy

        # Strategy 2: Look for the description of the first search result
        try:
            description_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='result-description']")))
            description = description_element.text
            if description:
                return jsonify({ "description": description })
        except (TimeoutException, NoSuchElementException):
            pass # If it fails, we will go to the final error

        return jsonify({ "error": "All lookup strategies failed." }), 404

    except Exception as e:
        return jsonify({ "error": f"An unexpected error occurred: {str(e)}" }), 500
    finally:
        if driver:
            driver.quit()