from .titles import titles
from .keywords import keywords
from .texts import texts
from .recitals import recitals

# Make sure all keys are strings and match across all sources
all_keys = set(titles.keys()) | set(keywords.keys()) | set(texts.keys()) | set(recitals.keys())

articles = {}

for key in sorted(all_keys):
    articles[key] = {
        "title": titles.get(key, "[Title Missing]"),
        "keywords": keywords.get(key, []),
        "text": texts.get(key, "[Text Missing]"),
        "recitals": recitals.get(key, []),
    }
