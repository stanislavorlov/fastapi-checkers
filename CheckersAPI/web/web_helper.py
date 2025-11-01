def parse_accept_language(header: str) -> str:
    """
    Parse Accept-Language header and return the top language code (e.g. 'en-US', 'uk', etc.)
    """
    if not header:
        return "en"  # default

    # Split by commas and sort by quality (q=)
    languages = []
    for part in header.split(","):
        lang_q = part.strip().split(";q=")
        lang = lang_q[0]
        q = float(lang_q[1]) if len(lang_q) == 2 else 1.0
        languages.append((lang, q))

    # Sort descending by q-value
    languages.sort(key=lambda x: x[1], reverse=True)

    return languages[0][0] if languages else "en"