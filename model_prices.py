"""
Static price and rating data for all 40 laptop models.
Used by load_data() to enrich the models DataFrame.
Keys are clean model names matching the filename stems in amazon_final_files/.
"""

MODEL_PRICE_RATING = {
    # ── ASUS ──────────────────────────────────────────────────────────────
    "ASUS VivoBook 15 X1502ZA":      {"price": 52990,  "rating": 4.0},
    "ASUS VivoBook Go 15 E1504FA":   {"price": 30990,  "rating": 4.2},
    "ASUS VivoBook 16 X1605":        {"price": 54990,  "rating": 4.3},
    "ASUS ZenBook 14 OLED":          {"price": 89990,  "rating": 4.5},
    "ASUS TUF F15 FX506":            {"price": 69990,  "rating": 4.4},
    "ASUS TUF A15 FA506":            {"price": 72990,  "rating": 4.4},
    "ASUS TUF F15 FX507":            {"price": 79990,  "rating": 4.5},
    "ASUS ROG Strix G15":            {"price": 119990, "rating": 4.6},
    "ASUS ROG Zephyrus G14":         {"price": 149990, "rating": 4.6},
    "ASUS ROG Strix Scar 15":        {"price": 229990, "rating": 4.7},

    # ── HP ────────────────────────────────────────────────────────────────
    "HP 15s-fq Series":              {"price": 42990,  "rating": 4.2},
    "HP 15s-eq Series":              {"price": 39990,  "rating": 4.1},
    "HP Pavilion 15-eg":             {"price": 63990,  "rating": 4.3},
    "HP Pavilion Aero 13":           {"price": 74990,  "rating": 4.4},
    "HP Victus 15":                  {"price": 64990,  "rating": 4.4},
    "HP Victus 16":                  {"price": 79990,  "rating": 4.5},
    "HP Victus 16 RTX 4050":         {"price": 94990,  "rating": 4.5},
    "HP Omen 16":                    {"price": 109990, "rating": 4.6},
    "HP Omen Transcend 14":          {"price": 149990, "rating": 4.6},
    "HP Omen 17":                    {"price": 179990, "rating": 4.6},

    # ── Dell ──────────────────────────────────────────────────────────────
    "Dell Inspiron 15 3520":         {"price": 49990,  "rating": 4.2},
    "Dell Vostro 15 3520":           {"price": 46990,  "rating": 4.1},
    "Dell Inspiron 14 5430":         {"price": 69990,  "rating": 4.3},
    "Dell Inspiron 14 7430":         {"price": 89990,  "rating": 4.4},
    "Dell G15 5520":                 {"price": 89990,  "rating": 4.4},
    "Dell G15 5530":                 {"price": 102990, "rating": 4.5},
    "Dell G15 5530 RTX 4050":        {"price": 115990, "rating": 4.5},
    "Dell G16":                      {"price": 129990, "rating": 4.5},
    "Dell XPS 15":                   {"price": 189990, "rating": 4.6},
    "Dell Alienware m16":            {"price": 229990, "rating": 4.6},

    # ── Lenovo ────────────────────────────────────────────────────────────
    "Lenovo IdeaPad Slim 3":         {"price": 49990,  "rating": 4.2},
    "Lenovo IdeaPad 3":              {"price": 42990,  "rating": 4.1},
    "Lenovo IdeaPad Slim 5":         {"price": 64990,  "rating": 4.3},
    "Lenovo Yoga Slim 6":            {"price": 82990,  "rating": 4.4},
    "Lenovo IdeaPad Gaming 3":       {"price": 74990,  "rating": 4.4},
    "Lenovo LOQ 15":                 {"price": 79990,  "rating": 4.4},
    "Lenovo LOQ 16":                 {"price": 89990,  "rating": 4.5},
    "Lenovo Legion 5":               {"price": 109990, "rating": 4.6},
    "Lenovo Legion Slim 7":          {"price": 159990, "rating": 4.6},
    "Lenovo Legion Pro 7":           {"price": 219990, "rating": 4.7},
}


def get_price_rating(model_name: str) -> dict:
    """
    Lookup price and rating for a model name.
    Uses exact match first, then normalised partial match.
    Returns {'price': float, 'rating': float} or {'price': None, 'rating': None}.
    """
    def normalise(s):
        # strip punctuation, lowercase, collapse spaces
        import re
        return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', s.lower())).strip()

    # Exact match
    if model_name in MODEL_PRICE_RATING:
        return MODEL_PRICE_RATING[model_name]

    # Case-insensitive exact
    lower = model_name.lower()
    for key, val in MODEL_PRICE_RATING.items():
        if key.lower() == lower:
            return val

    # Normalised partial match
    norm_input = normalise(model_name)
    best_key = None
    best_len = 0
    for key, val in MODEL_PRICE_RATING.items():
        norm_key = normalise(key)
        # Check if either contains the other
        if norm_key in norm_input or norm_input in norm_key:
            # Prefer the longest matching key to avoid false positives
            if len(norm_key) > best_len:
                best_len = len(norm_key)
                best_key = key
    if best_key:
        return MODEL_PRICE_RATING[best_key]

    # Token overlap fallback — match if ≥2 tokens overlap
    input_tokens = set(norm_input.split())
    best_overlap = 0
    for key, val in MODEL_PRICE_RATING.items():
        key_tokens = set(normalise(key).split())
        overlap = len(input_tokens & key_tokens)
        if overlap >= 2 and overlap > best_overlap:
            best_overlap = overlap
            best_key = key
    if best_key:
        return MODEL_PRICE_RATING[best_key]

    return {"price": None, "rating": None}
