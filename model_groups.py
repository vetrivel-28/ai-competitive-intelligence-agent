"""
Specification-Based Model Groupings
Maps laptop models into comparable groups by specification tier.
Each group contains rows of competing models across brands (ASUS, HP, Dell, Lenovo).
"""

# Key format: "Brand_ModelName" (underscores replace spaces)
# Each Row within a group contains models with similar specs across brands.

GROUPS = {
    "Group_1_Budget_Student": {
        "Row_1": ["ASUS VivoBook 15 X1502ZA",  "HP 15s-fq Series",       "Dell Inspiron 15 3520",  "Lenovo IdeaPad Slim 3"],
        "Row_2": ["ASUS VivoBook Go 15 E1504FA","HP 15s-eq Series",       "Dell Vostro 15 3520",    "Lenovo IdeaPad 3"],
    },
    "Group_2_Midrange_Thin_Light": {
        "Row_1": ["ASUS VivoBook 16 X1605",     "HP Pavilion 15-eg",      "Dell Inspiron 14 5430",  "Lenovo IdeaPad Slim 5"],
        "Row_2": ["ASUS ZenBook 14 OLED",       "HP Pavilion Aero 13",    "Dell Inspiron 14 7430",  "Lenovo Yoga Slim 6"],
    },
    "Group_3_Entry_Gaming": {
        "Row_1": ["ASUS TUF F15 FX506",         "HP Victus 15",           "Dell G15 5520",          "Lenovo IdeaPad Gaming 3"],
        "Row_2": ["ASUS TUF A15 FA506",         "HP Victus 16",           "Dell G15 5530",          "Lenovo LOQ 15"],
    },
    "Group_4_Mid_Gaming": {
        "Row_1": ["ASUS TUF F15 FX507",         "HP Victus 16 RTX 4050",  "Dell G15 5530 RTX 4050", "Lenovo LOQ 16"],
        "Row_2": ["ASUS ROG Strix G15",         "HP Omen 16",             "Dell G16",               "Lenovo Legion 5"],
    },
    "Group_5_Premium_Performance": {
        "Row_1": ["ASUS ROG Zephyrus G14",      "HP Omen Transcend 14",   "Dell XPS 15",            "Lenovo Legion Slim 7"],
        "Row_2": ["ASUS ROG Strix Scar 15",     "HP Omen 17",             "Dell Alienware m16",     "Lenovo Legion Pro 7"],
    },
}

# Brand mapping — which brand owns each model prefix
BRAND_MAP = {
    "ASUS":   "ASUS",
    "HP":     "HP",
    "Dell":   "Dell",
    "Lenovo": "Lenovo",
}


def get_brand(model_name: str) -> str:
    """Infer brand from model name string."""
    for prefix, brand in BRAND_MAP.items():
        if model_name.startswith(prefix):
            return brand
    return "Unknown"


def get_spec_group(model_name: str) -> tuple[str, str] | tuple[None, None]:
    """
    Given a model name, return (group_name, row_key) it belongs to.
    Returns (None, None) if not found.
    Uses fuzzy partial matching so 'ASUS VivoBook 15' matches 'ASUS VivoBook 15 X1502ZA'.
    """
    model_lower = model_name.lower()
    for group_name, rows in GROUPS.items():
        for row_key, models in rows.items():
            for m in models:
                if model_lower in m.lower() or m.lower() in model_lower:
                    return group_name, row_key
    return None, None


def get_spec_peers(model_name: str) -> list[dict]:
    """
    Return list of peer models (same spec group + row) for a given model.
    Each entry: {'model': str, 'brand': str}
    Excludes the model itself.
    """
    group_name, row_key = get_spec_group(model_name)
    if group_name is None:
        return []
    peers = []
    for m in GROUPS[group_name][row_key]:
        if m.lower() != model_name.lower():
            peers.append({'model': m, 'brand': get_brand(m)})
    return peers


def get_group_label(model_name: str) -> str:
    """Return a human-readable group label for a model."""
    group_name, _ = get_spec_group(model_name)
    if group_name is None:
        return "Ungrouped"
    return group_name.replace("_", " ")
