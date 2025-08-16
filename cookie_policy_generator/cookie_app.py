from flask import Blueprint, render_template, request, jsonify
from .scanner.cookie_scanner import extract_cookies_from_url
from .generator.policy_generator import generate_policy
import os

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