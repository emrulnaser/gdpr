from flask import Blueprint, render_template

cmp_bp = Blueprint(
    'cmp',
    __name__,
    template_folder='templates',
)

@cmp_bp.route('/')
def cmp_interface():
    return render_template('cmp_interface.html')
