# consent_mode_v2/consent_report.py

def generate_consent_report(url, scan_results):
    """Generate a report from the combined (static + Java) scan results."""
    if scan_results.get("status") == "error":
        return {
            "status": "error",
            "message": scan_results.get("message", "An unknown error occurred.")
        }

    # Extract signals and compliance from the new structure
    signals = scan_results.get("signals", {})
    compliance = scan_results.get("compliance", False)
    notes = scan_results.get("notes", "")

    # Create a simplified view for the template
    display_signals = {}
    for signal, checks in signals.items():
        # Prioritize Java result, fall back to static, then to "not found"
        static_res = checks.get("static_html", "not found")
        java_res = checks.get("java_selenium", "not found")
        
        final_status = "not found"
        if java_res != "not found":
            final_status = java_res
        elif static_res != "not found":
            final_status = static_res
            
        display_signals[signal] = final_status

    return {
        "status": "success",
        "website": url,
        "signals": display_signals,  # Simplified for the template
        "compliance": compliance,
        "notes": notes
    }