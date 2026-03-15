"""
Competitive Intelligence Engine
Step 1 — Target Company Configuration
"""

# All known brands in the market
ALL_BRANDS = ["ASUS", "HP", "Lenovo", "Dell", "Apple", "MSI", "Acer"]

# Default target company
target_company = "ASUS"

# Defined competitor pool
COMPETITOR_POOL = ["HP", "Lenovo", "Dell", "Apple"]


def get_competitors(target=None):
    """Return competitor brands for the given target, excluding the target itself."""
    if target is None:
        target = target_company
    return [brand for brand in COMPETITOR_POOL if brand.lower() != target.lower()]


def set_target_company(new_target):
    """Dynamically update the target company."""
    global target_company
    if new_target not in ALL_BRANDS:
        raise ValueError(f"Unknown brand '{new_target}'. Choose from: {ALL_BRANDS}")
    target_company = new_target


def get_config():
    """Return current configuration as a dict."""
    return {
        "target_company": target_company,
        "competitors": get_competitors(),
        "all_brands": ALL_BRANDS,
    }


if __name__ == "__main__":
    print("Target Company:", target_company)
    print("Competitors   :", get_competitors())
    set_target_company("HP")
    print("After switch  :", get_config())
