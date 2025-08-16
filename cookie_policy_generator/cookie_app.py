from flask import Blueprint, render_template, request, jsonify
from .scanner.cookie_scanner import extract_cookies_from_url
from .generator.policy_generator import generate_policy

# Playwright imports
from playwright.sync_api import sync_playwright
import time
import os

# Ensure Playwright uses local browser folder
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

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
    # cookies = extract_cookies_from_url(url)
    cookies = [{'name': 'dummy_cookie', 'domain': 'example.com', 'expiry': 'session', 'description': 'This is a dummy cookie.'}]
    policy = generate_policy(cookies)
    return render_template("cookie_policy_result.html", policy=policy, site=url)

# @cookie_bp.route("/lookup-cookie-api", methods=["POST"])
# def lookup_cookie_api():
#     cookie_name = request.json.get("cookie_name")
#     if not cookie_name:
#         return jsonify({ "error": "Cookie name is required." }), 400
#
#     try:
#         with sync_playwright() as p:
#             browser = p.chromium.launch(headless=True)
#             context = browser.new_context(
#                 user_agent=(
#                     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#                 )
#             )
#             page = context.new_page()
#             url = f"https://duckduckgo.com/?q=what+is+the+{cookie_name}+cookie&ia=web"
#             page.goto(url, wait_until="domcontentloaded", timeout=15000)
#
#             description = None
#
#             # Strategy 1: Search Assist definition
#             try:
#                 description_element = page.wait_for_selector(".search-assist-result__description", timeout=5000)
#                 description = description_element.inner_text()
#                 if description:
#                     browser.close()
#                     return jsonify({ "description": description })
#             except:
#                 pass
#
#             # Strategy 2: First search result description
#             try:
#                 description_element = page.wait_for_selector("[data-testid='result-description']", timeout=5000)
#                 description = description_element.inner_text()
#                 if description:
#                     browser.close()
#                     return jsonify({ "description": description })
#             except:
#                 pass
#
#             browser.close()
#             return jsonify({ "error": "All lookup strategies failed." }), 404
#
#     except Exception as e:
#         return jsonify({ "error": f"An unexpected error occurred: {str(e)}" }), 500
