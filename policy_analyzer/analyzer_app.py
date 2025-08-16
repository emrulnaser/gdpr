from flask import Blueprint, render_template

analyzer_bp = Blueprint(
    'analyzer',
    __name__,
    template_folder='templates',
)

@analyzer_bp.route('/')
def analyzer():
    return render_template('analyzer.html')
