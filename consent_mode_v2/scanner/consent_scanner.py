# consent_mode_v2/scanner/consent_scanner.py
from .utils import fetch_page_source
import re
import subprocess
import os

CONSENT_SIGNALS = [
    "ad_storage",
    "analytics_storage",
    "ad_user_data",
    "ad_personalization"
]

def scan_consent_mode(url):
    """Scan page for Google Consent Mode v2 signals in static HTML."""
    html = fetch_page_source(url)
    if html.startswith("ERROR:"):
        return {"error": html}

    results = {}
    for signal in CONSENT_SIGNALS:
        pattern = re.compile(rf"['\"]{signal}['\"]\s*:\s*['\"](granted|denied)['\"]", re.IGNORECASE)
        match = pattern.search(html)
        results[signal] = match.group(1).lower() if match else "not found"
    
    return results

def run_java_scanner(url):
    """Run the external Java scanner and return its console output."""
    # Adjust this path to where ConsentScanner.class and lib folder reside
    workdir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    jars = [
        "selenium-java-4.22.0.jar",
        "webdrivermanager-5.9.0.jar",
        "selenium-api-4.22.0.jar",
        "selenium-chrome-driver-4.22.0.jar",
        "selenium-chromium-driver-4.22.0.jar",
        "selenium-devtools-v124-4.22.0.jar",
        "selenium-devtools-v125-4.22.0.jar",
        "selenium-devtools-v126-4.22.0.jar",
        "selenium-devtools-v85-4.22.0.jar",
        "selenium-edge-driver-4.22.0.jar",
        "selenium-firefox-driver-4.22.0.jar",
        "selenium-http-4.22.0.jar",
        "selenium-ie-driver-4.22.0.jar",
        "selenium-json-4.22.0.jar",
        "selenium-manager-4.22.0.jar",
        "selenium-os-4.22.0.jar",
        "selenium-remote-driver-4.22.0.jar",
        "selenium-safari-driver-4.22.0.jar",
        "selenium-support-4.22.0.jar",
        "auto-service-annotations-1.1.1.jar",
        "byte-buddy-1.14.17.jar",
        "checker-qual-3.42.0.jar",
        "commons-exec-1.4.0.jar",
        "error_prone_annotations-2.27.0.jar",
        "failsafe-3.3.2.jar",
        "failureaccess-1.0.2.jar",
        "guava-33.2.1-jre.jar",
        "j2objc-annotations-3.0.0.jar",
        "jsr305-3.0.2.jar",
        "listenablefuture-9999.0-empty-to-avoid-conflict-with-guava.jar",
        "opentelemetry-api-1.39.0.jar",
        "opentelemetry-api-incubator-1.39.0-alpha.jar",
        "opentelemetry-context-1.39.0.jar",
        "opentelemetry-exporter-logging-1.39.0.jar",
        "opentelemetry-sdk-1.39.0.jar",
        "opentelemetry-sdk-common-1.39.0.jar",
        "opentelemetry-sdk-extension-autoconfigure-1.39.0.jar",
        "opentelemetry-sdk-extension-autoconfigure-spi-1.39.0.jar",
        "opentelemetry-sdk-logs-1.39.0.jar",
        "opentelemetry-sdk-metrics-1.39.0.jar",
        "opentelemetry-sdk-trace-1.39.0.jar",
        "opentelemetry-semconv-1.25.0-alpha.jar",
    ]
    classpath = ".;" + ";".join([os.path.join("lib", jar) for jar in jars])

    cmd = ["java", "-cp", classpath, "ConsentScanner", url]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=workdir, timeout=60)
        output = result.stdout.strip()
    except Exception as e:
        output = f"Error running Java scanner: {e}"

    return output

def run_scan(url):
    """Run combined scanner (static HTML + Java Selenium) and return unified report."""

    # Run static HTML scan
    static_results = scan_consent_mode(url)

    # Run Java Selenium scanner
    java_output = run_java_scanner(url)

    # Parse Java output signals (simple parse: look for lines like "signal: found"/"signal: not found")
    java_signals = {}
    for line in java_output.splitlines():
        line = line.strip().lower()
        for signal in CONSENT_SIGNALS:
            if line.startswith(signal):
                # line format: "signal: found" or "signal: not found"
                parts = line.split(":")
                if len(parts) >= 2:
                    java_signals[signal] = parts[1].strip()
                else:
                    java_signals[signal] = "unknown"

    # Combine static and Java results in one dict
    combined_signals = {}
    for signal in CONSENT_SIGNALS:
        combined_signals[signal] = {
            "static_html": static_results.get(signal, "not found"),
            "java_selenium": java_signals.get(signal, "not found"),
        }

    # Determine compliance (very simple heuristic)
    compliance = all(
        (v["static_html"] == "granted" or v["java_selenium"] == "found")
        for v in combined_signals.values()
    )

    notes = (
        "Java scanner output:\n" + java_output
        if java_output and not java_output.startswith("Error")
        else "Java scanner failed or not run."
    )

    report = {
        "status": "ok",
        "signals": combined_signals,
        "compliance": compliance,
        "notes": notes,
    }
    return report
