from flask import Blueprint, render_template

audit_bp = Blueprint(
    'audit',
    __name__,
    template_folder='templates',
)

@audit_bp.route('/')
def audit_log():
    return render_template('audit_log.html')
