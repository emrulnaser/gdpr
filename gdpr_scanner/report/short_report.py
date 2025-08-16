# policy/short_report.py

def run_short_scan(scan_results, t):
    """
    Generate summary text, total compliance score, and list of key non-compliant issues
    from the full scan results, focusing only on specific articles.

    Args:
        scan_results (dict): The full result dictionary from GDPRComplianceChecker.check_compliance().

    Returns:
        dict: A dictionary containing:
            - 'summary_text': Short report summary.
            - 'total_score': Compliance percentage score.
            - 'key_issues': List of non-compliant article titles from filtered articles.
            - 'full_report': The filtered scan_results for detailed display.
    """
    # Define the target articles for the short report
    TARGET_ARTICLES = ["Article 5", "Article 6", "Article 12", "Article 13", "Article 15", "Article 25", "Article 30"]

    # Create a new dictionary with only the target articles
    filtered_scan_results = {}
    for article_id in TARGET_ARTICLES:
        if article_id in scan_results:
            filtered_scan_results[article_id] = scan_results[article_id]

    # Initialize counts for filtered articles
    compliant_articles_count = 0
    partially_compliant_articles_count = 0
    non_compliant_articles_count = 0
    total_weighted_score = 0
    total_weight = 0

    # Define a local mapping for KEY_ISSUES relevant to the short report
    # This is a simplified version based on the articles requested.
    FILTERED_KEY_ISSUES_MAP = {
        "Article 5": "Processing",
        "Article 6": "Consent",
        "Article 12": "Right to be Informed (General)", # Article 12 is not a KEY_ISSUE in checker.py, mapping for display
        "Article 13": "Right to be Informed",
        "Article 15": "Right of Access",
        "Article 25": "Privacy by Design",
        "Article 30": "Records of Processing Activities",
    }

    # Rebuild key_issues_list and calculate scores based on filtered_scan_results
    new_key_issues_list = []
    emoji_map = {"compliant": "✅", "partial": "⚠", "non-compliant": "❌"}

    for article_id, details in filtered_scan_results.items():
        if isinstance(details, dict): # Ensure 'details' is a dictionary
            status_text = details.get("status", "").lower()
            if "strongly aligned" in status_text:
                status_flag = "compliant"
            elif "partially aligned" in status_text:
                status_flag = "partial"
            elif "needs review" in status_text:
                status_flag = "non-compliant"
            else:
                status_flag = "unknown"
            
            # Update counts
            if status_flag == "compliant":
                compliant_articles_count += 1
            elif status_flag == "partial":
                partially_compliant_articles_count += 1
            elif status_flag == "non-compliant":
                non_compliant_articles_count += 1

            # Calculate weighted score for filtered articles (simplified weights)
            # Assign a weight of 2 if it's a key issue, 1 otherwise.
            weight = 2 if article_id in FILTERED_KEY_ISSUES_MAP else 1
            total_weight += weight
            
            if status_flag == "compliant":
                total_weighted_score += weight * 1.0
            elif status_flag == "partial":
                total_weighted_score += weight * 0.6
            else:
                total_weighted_score += weight * 0.1

            # Add all filtered articles to new_key_issues_list with their status
            if article_id in FILTERED_KEY_ISSUES_MAP:
                issue_name_key = FILTERED_KEY_ISSUES_MAP[article_id]
                issue_name = t['key_issues'].get(issue_name_key, issue_name_key) # Get translated key issue name
                
                # Determine the CSS class for coloring
                status_class = 'ok' if status_flag == 'compliant' else ('warning' if status_flag == 'partial' else 'risk')
                
                # Determine the text to display for the status
                display_status_text = t['status_aligned'] if status_flag == 'compliant' else (t['status_partially'] if status_flag == 'partial' else t['status_review'])
                
                new_key_issues_list.append(
                    f"{issue_name} ({article_id}): <span class=\"status-{status_class}\">{emoji_map.get(status_flag, '')} {display_status_text}</span>"
                )

    # Recalculate total compliance score based on filtered articles
    new_total_compliance_score = 0
    if total_weight > 0:
        new_total_compliance_score = round((total_weighted_score / total_weight) * 100)

    # Build the summary text
    risk_level = scan_results.get("Overall Compliance Summary", {}).get("🛡️ Risk Level", "Unknown")
    summary_notes = scan_results.get("Overall Compliance Summary", {}).get("📌 Summary Notes", "No specific summary notes.")

    summary_text = (
        f"{t['overall_compliance_score']} {new_total_compliance_score}%\n"
        f"{t['non_compliant_articles']}: {non_compliant_articles_count}\n"
        f"{t['risk_level']}: {risk_level}\n"
        f"{t['summary_notes']}: {summary_notes}"
    )

    return {
        "summary_text": summary_text,
        "total_score": new_total_compliance_score, # Use the new calculated score
        "key_issues": new_key_issues_list, # Use the new filtered key issues
        "full_report": filtered_scan_results, # Pass the filtered report for detailed display
        "non_compliant_articles": non_compliant_articles_count # Add this line
    }