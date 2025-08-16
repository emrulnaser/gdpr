import re
from .scoring import calculate_score_and_risk, calculate_total_compliance_score

KEY_ISSUES = {
    "Consent": "Article 6",
    "Data Protection Officer": "Article 37",
    "Email Marketing": "Article 7",
    "Encryption": "Article 32",
    "Fines / Penalties": "Article 83",
    "Personal Data": "Article 4",
    "Privacy by Design": "Article 25",
    "Privacy Impact Assessment": "Article 35",
    "Processing": "Article 5",
    "Records of Processing Activities": "Article 30",
    "Right of Access": "Article 15",
    "Right to be Forgotten": "Article 17",
    "Right to be Informed": "Article 13",
    "Third Countries": "Article 44",
}

class GDPRComplianceChecker:
    def __init__(self, language='en'):
        self.articles = self._get_articles_by_language(language)

    def _get_articles_by_language(self, language='en'):
        if language == 'nl':
            from .articles.keywords_nl import KEYWORDS_NL as keywords_nl
            from .articles.titles_nl import titles as titles_nl
            from .articles.texts_nl import texts_nl
            from .articles.recitals_nl import recitals as recitals_nl

            keywords = {key.replace('Artikel', 'Article'): value for key, value in keywords_nl.items()}
            titles = {key.replace('Artikel', 'Article'): value for key, value in titles_nl.items()}
            texts = {key.replace('Artikel', 'Article'): value for key, value in texts_nl.items()}
            recitals = {key.replace('Artikel', 'Article'): value for key, value in recitals_nl.items()}

        else:
            from .articles.keywords import keywords
            from .articles.titles import titles
            from .articles.texts import texts
            from .articles.recitals import recitals

        
        articles = {}
        all_article_keys = set(keywords.keys()) | set(titles.keys()) | set(texts.keys()) | set(recitals.keys())

        for key in all_article_keys:
            articles[key] = {
                "keywords": keywords.get(key, []),
                "title": titles.get(key, ""),
                "text": texts.get(key, ""),
                "recitals": recitals.get(key, [])
            }
        return articles

    def _prepare_keywords_for_regex(self, keywords):
        patterns = []
        for kw in keywords:
            kw_lower = kw.lower()
            patterns.append(rf'\b{re.escape(kw_lower)}(s)?\b')

            if kw_lower == "consent":
                patterns.extend([rf'\b(consent|agree(ment)?|permission|opt-in|opt out)\b'])
            elif kw_lower == "right to be forgotten":
                patterns.extend([rf'\b(erasure|delete|remove|right to be forgotten)\b', rf'\b(delete|remove) your (data|information|account)\b'])
            elif kw_lower == "data breach":
                patterns.extend([rf'\b(data breach|security breach|security incident|unauthorised access)\b'])
            elif kw_lower == "data portability":
                patterns.extend([rf'\b(data portability|transfer your data|move your data|data transfer)\b'])
            elif kw_lower == "right of access":
                patterns.extend([rf'\b(right of access|access your data|access to information|subject access request)\b'])
            elif kw_lower == "data minimisation":
                patterns.extend([rf'\b(data minimi[sz]ation|only necessary data|limit data collection)\b'])
            elif kw_lower == "privacy by design":
                patterns.extend([rf'\b(privacy by design|data protection by design|privacy by default)\b'])
            elif kw_lower == "third countries":
                patterns.extend([rf'\b(third countr(y|ies)|international transfers?|outside the (EU|EEA))\b', rf'\b(standard contractual clauses|SCCs)\b'])

        return [re.compile(p, re.IGNORECASE) for p in set(patterns)]

    def _fuzzy_match(self, text, keywords):
        matched_terms = set()
        text_lower = text.lower()
        text_words = set(re.findall(r'\b\w+\b', text_lower))

        for kw in keywords:
            kw_lower = kw.lower()
            kw_words = set(re.findall(r'\b\w+\b', kw_lower))

            # Check if the entire keyword phrase is present as a substring
            if kw_lower in text_lower:
                matched_terms.add(kw)
            else:
                # Check if a significant portion of the keyword's words are present
                # This is a more lenient "fuzzy" match
                common_words = kw_words.intersection(text_words)
                if len(common_words) >= len(kw_words) / 2:  # At least half the words match
                    matched_terms.add(kw)

        return len(matched_terms), list(matched_terms)

    def check_compliance(self, text, t):
        results = {}
        key_issues_result = []
        compliant_articles_count, partially_compliant_articles_count, non_compliant_articles_count = 0, 0, 0
        fully_compliant_articles = []
        weighted_score_total, weight_sum = 0, 0

        for article_id, data in self.articles.items():
            keywords = data.get("keywords", [])
            
            # Initialize status and match_percent for all articles
            status, status_flag, match_percent = "⚪ No Keywords Defined", "no_keywords", 0
            matched_count = 0
            found_terms_list = []

            if keywords: # Only perform matching if keywords are defined for the article
                matched_count, found_terms_list = self._fuzzy_match(text, keywords)
                
                # Simplified scoring logic based on keyword counts, as requested.
                if matched_count >= 3:
                    status, status_flag, match_percent = f"✅ {t['status_aligned']}", "compliant", 100
                elif matched_count == 2:
                    status, status_flag, match_percent = f"⚠ {t['status_partially']}", "partial", 50
                else: # Covers 0 or 1 match
                    status, status_flag, match_percent = f"❌ {t['status_review']}", "non-compliant", 15 if matched_count == 1 else 0
            
            # Update counts for overall summary
            if status_flag == "compliant":
                compliant_articles_count += 1
                fully_compliant_articles.append(article_id)
            elif status_flag == "partial":
                partially_compliant_articles_count += 1
            elif status_flag == "non-compliant":
                non_compliant_articles_count += 1

            # Define weight and add to total for overall score calculation
            weight = 2 if article_id in KEY_ISSUES.values() else 1
            weight_sum += weight
            if status_flag == "compliant":
                weighted_score_total += weight * 1.0
            elif status_flag == "partial":
                weighted_score_total += weight * 0.6
            else:
                weighted_score_total += weight * 0.1

            results[article_id] = {
                "title": data.get("title", ""),
                "found_terms": found_terms_list,
                "match_percentage": f"{match_percent}%",
                "status": status,
                "summary": data.get("text", ""),
                "recitals": data.get("recitals", [])
            }

            # Populate key_issues_result only for articles in KEY_ISSUES
            for issue_name, aid in KEY_ISSUES.items():
                if aid == article_id:
                    key_issues_result.append({
                        "name": issue_name,
                        "article": aid,
                        "status": status_flag
                    })

        # ✅ Round the general article score
        # 🔍 Calculate Key Issue Compliance Score
        key_issue_total = len(KEY_ISSUES)
        key_issue_score_total = 0
        for item in key_issues_result:
            if item["status"] == "compliant":
                key_issue_score_total += 1.0
            elif item["status"] == "partial":
                key_issue_score_total += 0.6
            # non-compliant gives 0

        key_issue_compliance_score = round((key_issue_score_total / key_issue_total) * 100)

        # 🔎 Use risk level and summary as before
        key_issue_score, risk_level, issue_summary = calculate_score_and_risk(key_issues_result, t)

        overall_article_score = key_issue_score

        total_compliance_score = calculate_total_compliance_score(compliant_articles_count, partially_compliant_articles_count)

        results["Overall Compliance Summary"] = {
            "📌 Article Score": f"{overall_article_score}%",
            "✅ Key Issues Score": f"{key_issue_score}%",
            "📈 Key Issues Compliance Score": f"{key_issue_compliance_score}%",  # NEW
            "🛡️ Risk Level": risk_level,
            "📌 Summary Notes": issue_summary,
            "📊 Compliance Breakdown": {
                "Compliant Articles": compliant_articles_count,
                "Partially Compliant Articles": partially_compliant_articles_count,
                "Requires Review Articles": non_compliant_articles_count
            },
            "Total Compliance Score": total_compliance_score
        }

        results["Fully Compliant Articles List"] = sorted(fully_compliant_articles, key=lambda x: int(x.split(' ')[1]))

        # Sorted Key Issues View
        emoji = {"compliant": "✅", "partial": "⚠", "non-compliant": "❌"}
        key_issues_result.sort(key=lambda x: int(x['article'].split(' ')[1]))
        results["Key Issues"] = [
            f"{idx+1}) {item['name']} ({item['article']}): {emoji.get(item['status'], '')} {'Strongly Aligned' if item['status'] == 'compliant' else ('Partially Aligned' if item['status'] == 'partial' else item['status'].capitalize())}"
            for idx, item in enumerate(key_issues_result)
        ]
        return results