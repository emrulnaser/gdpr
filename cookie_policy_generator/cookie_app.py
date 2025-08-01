from flask import Blueprint, render_template

cookie_bp = Blueprint(
    'cookie',
    __name__,
    template_folder='templates',
)

@cookie_bp.route('/')
def cookie_policy():
    return render_template('generator.html')
