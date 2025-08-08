# consent_mode_v2/consent_app.py
from flask import Blueprint, render_template, request, redirect, url_for
from .scanner.consent_scanner import run_scan  # Updated import
from .consent_report import generate_consent_report

consent_bp = Blueprint('consent', __name__, template_folder='templates')

@consent_bp.route('/', methods=['GET', 'POST'])
def consent_checker():
    if request.method == 'POST':
        url = request.form.get('website_url', '').strip()
        if url:
            return redirect(url_for('consent.consent_report', website_url=url))
    return render_template('consent_checker.html')

@consent_bp.route('/test_page')
def test_page():
    return render_template('test_consent.html')

@consent_bp.route('/report')
def consent_report():
    website_url = request.args.get('website_url')
    if not website_url:
        return redirect(url_for('consent.consent_checker'))

    # Use the combined scanner for more accurate results
    scan_results = run_scan(website_url)
    
    # The report generation might need adjustment if the structure of scan_results changed.
    # For now, we assume generate_consent_report can handle the new structure.
    report_data = generate_consent_report(website_url, scan_results)
    
    return render_template('consent_report.html',
                           website_url=website_url,
                           report=report_data)
