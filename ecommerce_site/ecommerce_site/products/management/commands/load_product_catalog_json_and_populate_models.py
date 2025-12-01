import json
import os
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import (
    BaseCommand, CommandError
)
from django.db import transaction

from products.choices import SizeChoices
from products.models import (
    Category,
    Product,
    ProductDetail,
    ProductImage
)
from .mappings import (
    CATEGORY_MAPPING,
    DEFAULT_SIZE,
    DEFAULT_STOCK,
    PRODUCT_MATERIALS
)


class Command(BaseCommand):
    help = (
        "Imports product data from the 'clothes.json' file. This process involves cleaning price "
        "formats, automatically assigning categories based on product name keywords, and "
        "performing atomic Create or Update (CRUD) operations on the Product, ProductDetail, "
        "and ProductImage models to ensure data consistency and integrity."
    )

    def get_category_from_product_name(self, product_name):
        assigned_category_name = next(
            (
                category_name
                for category_identifier, category_name in CATEGORY_MAPPING.items()
                if category_identifier != "OTHERS"
                   and category_identifier in product_name.upper()
            ),
            CATEGORY_MAPPING["OTHERS"]
        )

        return assigned_category_name

    def get_product_material(self, product_details):
        product_material_details = " ".join(product_details).upper()

        return next(
            (
                product_material
                for product_material in PRODUCT_MATERIALS
                if product_material.upper() in product_material_details
            ),
            "N/A"
        )

    def handle(self, *args, **options):
        json_file_path = (
                Path(os.path.abspath(__file__)).parent.parent / "data" / "clothes.json"
        )

        self.stdout.write(f"Starting product data import from {json_file_path}")

        try:
            with open(json_file_path, "r", encoding="utf-8") as json_file:
                product_data_list = json.load(json_file)
        except json.JSONDecodeError:
            raise CommandError(
                "Error decoding JSON file. Check for syntax errors."
            )

        total_products_counter = len(product_data_list)
        success_imports_counter = 0

        with transaction.atomic():
            for product_json_record in product_data_list:
                try:
                    price_string = (
                        product_json_record.get("product_price", "0.00")
                        .replace("PKR\xa0", "")
                        .replace("PKR ", "")
                        .replace(",", "")
                        .strip()
                    )

                    try:
                        product_price = Decimal(price_string)
                    except InvalidOperation:
                        self.stdout.write(self.style.WARNING(
                            f"Skipping '{product_json_record.get('product_name')}': "
                            f"Invalid price format '{price_string}'"
                        ))
                        continue

                    product_name = product_json_record.get("product_name").strip()
                    product_code = product_json_record.get("product_code", product_name)

                    assigned_category_name = self.get_category_from_product_name(
                        product_name
                    )

                    product_category, category_created = Category.objects.get_or_create(
                        name=assigned_category_name
                    )

                    if category_created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f" Created new Category: {assigned_category_name}"
                            )
                        )

                    product_instance, _ = Product.objects.update_or_create(
                        code=product_code,
                        defaults={
                            "name": product_name,
                            "category": product_category,
                        }
                    )

                    product_info_list = product_json_record.get(
                        "product_info", []
                    )

                    ProductDetail.objects.update_or_create(
                        product=product_instance,
                        defaults={
                            "size": DEFAULT_SIZE,
                            "material": self.get_product_material(product_info_list),
                            "color": product_info_list[0] if product_info_list else "N/A",
                            "stock": DEFAULT_STOCK,
                            "price": product_price,
                            "description": "\n".join(product_info_list),
                        }
                    )

                    for image_index, image_source_url in enumerate(
                        product_json_record.get("product_images", [])
                    ):
                        ProductImage.objects.update_or_create(
                            url=image_source_url,
                            defaults={
                                "product": product_instance,
                                "alt_text": f"{product_name} - Image {image_index + 1}",
                            }
                        )

                    success_imports_counter += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  [SUCCESS] Product: {product_name} ({product_category.name})"
                        )
                    )

                except Exception as error:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Failed to process product: "
                            f"{product_json_record.get('product_name', 'N/A')}. "
                            f"Error: {error}"
                        )
                    )

        self.stdout.write("\n")
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {success_imports_counter}/{total_products_counter} products."
            )
        )
