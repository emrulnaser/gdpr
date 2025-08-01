from flask import Blueprint, render_template

scanner_bp = Blueprint(
    'scanner',
    __name__,
    template_folder='templates',
)

@scanner_bp.route('/')
def scanner_report():
    return render_template('scanner_report.html')
