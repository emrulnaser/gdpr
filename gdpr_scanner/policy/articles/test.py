from policy.gdpr_checker import GDPRComplianceChecker  # Adjust path if needed

# Sample test input text
text = """
The data subject has the right to transparent information and access to personal data.
Controllers must ensure fairness, transparency, and appropriate safeguards in data processing.
"""

# Sample keywords (e.g., from Article 5 or 12)
keywords = [
    "transparent information", "fairness", "data subject", "processing", "safeguards",
    "personal data", "controller", "lawfulness"
]

# Create the checker instance
checker = GDPRComplianceChecker()

# Call _fuzzy_match directly
matched_count, found_terms_list = checker._fuzzy_match(text, keywords)

# Print results
print(f"Matched Count: {matched_count}")
print("Found Keywords:", found_terms_list)
