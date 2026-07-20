import json
from pathlib import Path

from retailmind_api.models import Product

CATALOG_PATH = Path(__file__).parent / "data" / "catalog.json"


def get_catalog() -> tuple[Product, ...]:
    """Load and validate the demo catalog so local product edits appear immediately."""
    with CATALOG_PATH.open(encoding="utf-8") as catalog_file:
        records = json.load(catalog_file)

    return tuple(Product.model_validate(record) for record in records)


def filter_catalog(
    *,
    category: str | None = None,
    material: str | None = None,
    occasion: str | None = None,
    max_price: int | None = None,
    size: str | None = None,
    in_stock: bool = True,
) -> list[Product]:
    products = get_catalog()

    def matches(product: Product) -> bool:
        if category and product.category.casefold() != category.casefold():
            return False
        if material and material.casefold() not in {item.casefold() for item in product.materials}:
            return False
        if occasion and occasion.casefold() not in {
            item.casefold() for item in product.occasions
        }:
            return False
        if max_price is not None and product.price > max_price:
            return False
        if size and size.casefold() not in {item.casefold() for item in product.sizes}:
            return False
        return not in_stock or product.total_stock > 0

    return [product for product in products if matches(product)]
