from flask import Blueprint, render_template, request, redirect, url_for, current_app, make_response
import weasyprint
import os
from werkzeug.utils import secure_filename

# Import logic from helper modules
from .report.short_report import run_short_scan
from .report.full_report import run_full_scan
from .policy.checker import GDPRComplianceChecker

gdpr_bp = Blueprint(
    'gdpr',
    __name__,
    template_folder='templates',
)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_uploaded_file(filepath):
    ext = filepath.rsplit('.', 1)[1].lower()
    content = ""
    try:
        if ext == 'txt' or ext == 'csv':
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        elif ext == 'pdf':
            import PyPDF2
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    content += page.extract_text() + "\n"
    except Exception as e:
        content = ""
    return content

@gdpr_bp.route('/')
def main_page():
    return render_template('Main_page.html')

from .translations import translations

@gdpr_bp.route('/scan', methods=['GET', 'POST'])
def scan():
    error = None
    results = {"summary_text": "", "total_score": 0, "key_issues": [], "full_report": {}}
    scanned_text = None
    language = request.form.get('selected_language', 'en')
    t = translations.get(language, translations['en'])

    if request.method == 'POST':
        input_text = request.form.get('text', '').strip()
        file = request.files.get('file', None)
        file_content = ""

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            file_content = read_uploaded_file(save_path)
            os.remove(save_path)

        combined_text = input_text + "\n" + file_content if input_text or file_content else None

        if not combined_text or combined_text.strip() == "":
            error = "Please provide some text or upload a valid file."
        else:
            checker = GDPRComplianceChecker(language=language)
            scan_results = checker.check_compliance(combined_text, t)
            results = run_short_scan(scan_results, t)
            scanned_text = combined_text

    return render_template(
        'short_report.html',
        results=results.get('full_report', {}),
        error=error,
        scanned_text=scanned_text,
        summary_text=results.get('summary_text', ''),
        total_score=results.get('total_score', 0),
        key_issues=results.get('key_issues', []),
        t=t
    )


from .translations import translations

@gdpr_bp.route('/full_report', methods=['GET', 'POST'])
def full_report():
    if request.method == 'GET':
        return redirect(url_for('gdpr.full_report_input'))

    error = None
    scanned_text = None
    language = request.form.get('selected_language', 'en')
    t = translations.get(language, translations['en'])

    overall_report = {
        "results": {},
        "key_issues": "",
        "score": 0,
        "risk_level": "Unknown",
        "summary": "",
        "total_compliance_score": "N/A",
        "compliant_articles": [],
        "partial_articles": [],
        "non_compliant_articles": []
    }

    input_text = request.form.get('text_input', '').strip()
    file = request.files.get('file_input', None)
    file_content = ""

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        file_content = read_uploaded_file(save_path)
        os.remove(save_path)

    combined_text = (input_text + "\n" + file_content).strip() if (input_text or file_content) else None

    if not combined_text:
        error = "Please provide some text or upload a valid file."
    else:
        checker = GDPRComplianceChecker(language=language)
        overall_report = run_full_scan(combined_text, checker, t)
        scanned_text = combined_text

    return render_template(
        'full_report.html',
        results=overall_report.get("results", {}),
        error=error,
        scanned_text=scanned_text,
        key_issues=overall_report.get('key_issues', ''),
        score=overall_report.get('score', 0),
        risk_level=overall_report.get('risk_level', 'Unknown'),
        summary=overall_report.get('summary', ''),
        total_compliance_score=overall_report.get('total_compliance_score', 'N/A'),
        compliant_articles=overall_report.get('compliant_articles', []),
        partial_articles=overall_report.get('partial_articles', []),
        non_compliant_articles=overall_report.get('non_compliant_articles', []),
        t=t
    )


@gdpr_bp.route('/full_report_input')
def full_report_input():
    return render_template('full_report_input.html')

@gdpr_bp.route('/download_pdf', methods=['POST'])
def download_pdf():
    # Retrieve the data needed for the report from the form
    scanned_text = request.form.get('scanned_text', '')
    language = request.form.get('selected_language', 'en')
    t = translations.get(language, translations['en'])
    
    # Regenerate the report data
    checker = GDPRComplianceChecker(language=language)
    overall_report = run_full_scan(scanned_text, checker, t)
    results = overall_report.get("results", {})

    # Render the HTML template with the data
    rendered_html = render_template(
        'full_report.html',
        results=results,
        scanned_text=scanned_text,
        key_issues=overall_report.get('key_issues', ''),
        score=overall_report.get('score', 0),
        risk_level=overall_report.get('risk_level', 'Unknown'),
        summary=overall_report.get('summary', ''),
        total_compliance_score=overall_report.get('total_compliance_score', 'N/A'),
        compliant_articles=overall_report.get('compliant_articles', []),
        partial_articles=overall_report.get('partial_articles', []),
        non_compliant_articles=overall_report.get('non_compliant_articles', []),
        t=t
    )

    # Generate PDF from the rendered HTML
    pdf = weasyprint.HTML(string=rendered_html).write_pdf()

    # Create a response with the PDF
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=GDPR_Full_Report.pdf'
    
    return response