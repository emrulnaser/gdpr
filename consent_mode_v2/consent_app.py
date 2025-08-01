from flask import Blueprint, render_template

consent_bp = Blueprint(
    'consent',
    __name__,
    template_folder='templates',
)

@consent_bp.route('/')
def consent_report():
    return render_template('consent_report.html')
