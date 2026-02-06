"""
Central brand/domain mapping for News Studio.
Used by UI and APIs to filter by domain and apply theme.
"""
from typing import TypedDict


class BrandConfig(TypedDict):
    domain: str
    display: str
    theme: str


BRANDS: dict[str, BrandConfig] = {
    "althara": {
        "domain": "real_estate",
        "display": "Althara",
        "theme": "althara",
    },
    "oxono": {
        "domain": "tech",
        "display": "Oxono",
        "theme": "oxono",
    },
}


def get_domain_for_brand(brand: str) -> str | None:
    """Returns domain string for brand, or None if unknown."""
    config = BRANDS.get(brand)
    return config["domain"] if config else None


def get_display_name(brand: str) -> str:
    """Returns display name for brand."""
    config = BRANDS.get(brand)
    return config["display"] if config else brand


def get_theme(brand: str) -> str:
    """Returns theme/css class for brand."""
    config = BRANDS.get(brand)
    return config["theme"] if config else "default"


def get_brand_for_domain(domain: str) -> str | None:
    """Returns brand key for domain, or None if unknown."""
    for brand, config in BRANDS.items():
        if config["domain"] == domain:
            return brand
    return None
