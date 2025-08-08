from ..policy.checker import GDPRComplianceChecker
import re

def run_full_scan(policy_text, checker, t):
    """
    Runs a full GDPR compliance scan and returns a detailed report.
    This function utilizes the centralized logic from the 'policy' package.
    """
    results = checker.check_compliance(policy_text, t)

    # Extract the summary data that checker.py already calculated
    summary_data = results.pop("Overall Compliance Summary", {})
    key_issues_list = results.pop("Key Issues", [])

    # Translate key issue names
    translated_key_issues_list = []
    for item_str in key_issues_list:
        # Example: "1) Personal Data (Article 4): ✅ Strongly Aligned"
        # Extract the key issue name, which is between the number and "(Article"
        match = re.match(r'^(\d+)\) (.*?) \((Article\s\d+)\): (.*)$', item_str)
        if match:
            num = match.group(1)
            original_name = match.group(2).strip()
            article_id = match.group(3).strip()
            status_part = match.group(4).strip()
            translated_name = t['key_issues'].get(original_name, original_name)
            
            # Translate the status part
            translated_status_part = status_part
            if "Strongly Aligned" in status_part:
                translated_status_part = status_part.replace("Strongly Aligned", t['status_aligned'])
            elif "Partially Aligned" in status_part:
                translated_status_part = status_part.replace("Partially Aligned", t['status_partially'])
            elif "Needs Review" in status_part:
                translated_status_part = status_part.replace("Needs Review", t['status_review'])
            
            translated_key_issues_list.append(f"{num}) {translated_name} ({article_id}): {translated_status_part}")
        else:
            translated_key_issues_list.append(item_str) # Fallback if regex doesn't match

    # The score from checker.py is a string like "85.5%", so we parse it
    article_score_str = summary_data.get("📌 Article Score", "0%")
    try:
        score = int(float(article_score_str.replace('%', '')))
    except ValueError:
        score = 0

    risk_level = summary_data.get("🛡️ Risk Level", "Unknown")
    summary_notes = summary_data.get("📌 Summary Notes", "Unable to generate summary.")
    total_compliance_score = summary_data.get("Total Compliance Score", "N/A")
    
    # Join the list of key issues into a single string for display
    key_issues_summary = "\n".join(translated_key_issues_list)

    # The rest of the 'results' dictionary is the article-by-article breakdown
    # Pop the Fully Compliant Articles List before sorting, as it's not an article
    fully_compliant_articles_list = results.pop("Fully Compliant Articles List", [])

    # Sort the articles by their number
    sorted_results = dict(sorted(results.items(), key=lambda item: int(item[0].split(' ')[1]) if item[0].startswith('Article') else 999))

    # Generate concise article compliance summary
    compliant_articles_nums = []
    partial_articles_nums = []
    non_compliant_articles_nums = []

    for article_id, data in sorted_results.items():
        if article_id.startswith("Article"):
            status = data.get("status", "")
            article_num = article_id.split(' ')[1]
            if "✅" in status:
                compliant_articles_nums.append(article_num)
            elif "⚠" in status:
                partial_articles_nums.append(article_num)
            elif "❌" in status:
                non_compliant_articles_nums.append(article_num)

    

    key_issues_summary = "\n".join(translated_key_issues_list)

    return {
        "key_issues": key_issues_summary,
        "score": score,
        "risk_level": risk_level,
        "summary": summary_notes,
        "total_compliance_score": total_compliance_score,
        "compliant_articles": compliant_articles_nums, # Separate list
        "partial_articles": partial_articles_nums,     # Separate list
        "non_compliant_articles": non_compliant_articles_nums, # Separate list
        "fully_compliant_articles_list": fully_compliant_articles_list, # Pass the new list
        "results": sorted_results
    }
