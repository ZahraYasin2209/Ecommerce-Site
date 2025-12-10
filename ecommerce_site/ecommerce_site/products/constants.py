from decimal import Decimal

PRODUCT_ORDER_MAPPING = {
    "price_low_to_high": "min_price",
    "price_high_to_low": "-min_price",
    "newest_first": "-created",
    "oldest_first": "created",
}

DEFAULT_MIN_PRICE = Decimal("900")
DEFAULT_MAX_PRICE = Decimal("75000")
