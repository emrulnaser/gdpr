def calculate_score_and_risk(key_issues, t):
    if not key_issues or not isinstance(key_issues, list):
        return 0, t['risk_critical'], f"❌ {t['summary_no_data']}"

    total_key_issues = len(key_issues)
    if total_key_issues == 0:
        return 100, t['risk_low'], f"✅ {t['summary_no_issues']}"

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
        risk = t['risk_very_low']
        summary = f"✅ {t['summary_excellent']}"
    elif final_score >= 75:
        risk = t['risk_low']
        summary = f"👍 {t['summary_strong']}"
    elif final_score >= 50:
        risk = t['risk_medium']
        summary = f"⚠️ {t['summary_moderate']}"
    elif final_score >= 25:
        risk = t['risk_high']
        summary = f"❌ {t['summary_significant']}"
    else:
        risk = t['risk_critical']
        summary = f"🚨 {t['summary_critical']}"

    # Escalate risk if critical issues are missed
    if critical_non_compliant_count > 0:
        if risk in [t['risk_very_low'], t['risk_low']]:
            risk = f"{t['risk_medium']} to {t['risk_high']}"
            summary += f"\n❗ {t['summary_critical_missed']}"
        elif risk == t['risk_medium']:
            risk = t['risk_high']
            summary += f"\n❗ {t['summary_critical_missed_escalated']}"

    return final_score, risk, summary

def calculate_total_compliance_score(compliant_articles_count, partially_compliant_articles_count):
    total_compliance_score = (compliant_articles_count * 1.04) + (partially_compliant_articles_count * 0.05)
    return f"{total_compliance_score:.2f}"