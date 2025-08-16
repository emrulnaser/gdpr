from flask import Flask, render_template
import os

# Suppress GTK warnings
os.environ['GDK_BACKEND'] = 'cairo'

# Import blueprints from each tool
from gdpr_scanner.gdpr_app import gdpr_bp

from cookie_policy_generator.cookie_app import cookie_bp
from consent_mode_v2.consent_app import consent_bp
from cookie_scanner.scanner_app import scanner_bp
from cmp_lite.cmp_app import cmp_bp
from audit_log_manager.audit_app import audit_bp
from policy_analyzer.analyzer_app import analyzer_bp

# --- App Configuration ---
app = Flask(__name__, template_folder='.') # Set template folder to the root
app.jinja_env.cache = None # Disable Jinja2 template caching
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
app.config['TEMPLATES_AUTO_RELOAD'] = True # Explicitly enable template auto-reloading
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 # Disable caching for static files

# --- Blueprint Registration ---
# Register the GDPR scanner blueprint under the '/gdpr' prefix
app.register_blueprint(gdpr_bp, url_prefix='/gdpr')

app.register_blueprint(cookie_bp, url_prefix='/cookie_policy_generator')
app.register_blueprint(consent_bp, url_prefix='/consent_mode_v2')
app.register_blueprint(scanner_bp, url_prefix='/cookie_scanner')
app.register_blueprint(cmp_bp, url_prefix='/cmp_lite')
app.register_blueprint(audit_bp, url_prefix='/audit_log_manager')
app.register_blueprint(analyzer_bp, url_prefix='/policy_analyzer')

# --- Main Route ---
@app.route('/')
def main_page():
    """Serves the main landing page for all tools."""
    return render_template('main_page.html')

# --- Main Execution ---
if __name__ == '__main__':
    # Create the upload directory if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Run the Flask application
    app.run(host='0.0.0.0', port=10000, debug=True)