def calculate_score_and_risk(key_issues):
    if not key_issues or not isinstance(key_issues, list):
        return 0, "Critical", "❌ No key issue data provided. Cannot assess compliance effectively."

    total_key_issues = len(key_issues)
    if total_key_issues == 0:
        return 100, "Low", "✅ No specific key issues identified for assessment (implies full coverage or no relevant content)."

    score_accumulator = 0
    critical_issues = {
        "Processing", "Consent", "Right to be Informed",
        "Right to be Forgotten", "Data Breach Notification",
        "Data Portability", "Data Minimisation", "Accountability",
        "Personal Data"
    }

    critical_non_compliant_count = 0
    non_critical_non_compliant_count = 0
    
    for issue in key_issues:
        status = issue.get("status")
        name = issue.get("name")

        if status == "compliant":
            score_accumulator += 1.0
        elif status == "partial":
            score_accumulator += 0.5
        else:  # non-compliant
            if name in critical_issues:
                critical_non_compliant_count += 1
            else:
                non_critical_non_compliant_count += 1

    # Base score from compliant + partial
    base_score = (score_accumulator / total_key_issues) * 100

    # New penalty logic — gentler, proportional penalties
    penalty = (critical_non_compliant_count * 5) + (non_critical_non_compliant_count * 2)
    
    final_score = base_score

    # Determine risk level and summary
    if final_score >= 90:
        risk = "Very Low"
        summary = "✅ Excellent GDPR alignment. Your policy appears highly compliant with key principles."
    elif final_score >= 75:
        risk = "Low"
        summary = "👍 Strong GDPR compliance. Minor adjustments may be beneficial."
    elif final_score >= 50:
        risk = "Medium"
        summary = "⚠️ Moderate GDPR compliance. Several key areas require review and potential enhancement."
    elif final_score >= 25:
        risk = "High"
        summary = "❌ Significant GDPR compliance gaps. Urgent review and substantial changes are recommended."
    else:
        risk = "Critical"
        summary = "🚨 Critical GDPR compliance issues detected. Immediate action is required to avoid severe penalties."

    # Escalate risk if critical issues are missed
    if critical_non_compliant_count > 0:
        if risk in ["Very Low", "Low"]:
            risk = "Medium to High"
            summary += "\n❗ Critical GDPR principles are not adequately addressed despite overall score."
        elif risk == "Medium":
            risk = "High"
            summary += "\n❗ Critical GDPR principles are not adequately addressed, increasing overall risk."

    return final_score, risk, summary

def calculate_total_compliance_score(compliant_articles_count, partially_compliant_articles_count):
    total_compliance_score = (compliant_articles_count * 1.04) + (partially_compliant_articles_count * 0.05)
    return f"{total_compliance_score:.2f}"