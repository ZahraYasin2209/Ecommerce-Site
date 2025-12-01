import json
import os
from decimal import Decimal, InvalidOperation

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
        "Reads product information from clothes.json and stores it across all product-related "
        "models in the database. This includes automatically detecting and assigning categories,"
        "creating or updating products, generating product details, saving product images, "
        "leaning price formats, and performing all operations inside an atomic transaction to "
        "maintain data integrity."
    )

    def get_category_from_product_name(self, product_name):
        assigned_category_name = CATEGORY_MAPPING["OTHERS"]

        for category_identifier, category_name in CATEGORY_MAPPING.items():
            if category_identifier == "OTHERS":
                continue

            if category_identifier in product_name.upper():
                assigned_category_name = category_name

        return assigned_category_name

    def get_product_material(self, product_details):
        found_product_material = "N/A"

        for product_material in PRODUCT_MATERIALS:
            if any(product_material in product_attribute
                   for product_attribute in product_details):
                found_product_material = product_material

        return found_product_material

    def handle(self, *args, **options):
        command_dir = os.path.dirname(os.path.abspath(__file__))

        data_dir = os.path.join(os.path.dirname(command_dir), "data")
        json_file_path = os.path.join(data_dir, "clothes.json")

        self.stdout.write(f"Starting product data import from {json_file_path}")

        try:
            with open(json_file_path, "r", encoding="utf-8") as json_file:
                product_data_list = json.load(json_file)
        except json.JSONDecodeError:
            raise CommandError(
                "Error decoding JSON file. Check for syntax errors."
            )
        except Exception as error:
            raise CommandError(f"An unexpected error occurred: {error}")

        total_products_counter = len(product_data_list)
        success_imports_counter = 0

        with transaction.atomic():
            for product_json_record in product_data_list:
                try:
                    price_string = product_json_record.get("product_price", "0.00")

                    cleaned_price_str = (
                        price_string.replace("PKR\xa0", "")
                        .replace("PKR ", "")
                        .replace(",", "")
                        .strip()
                    )

                    try:
                        product_price = Decimal(cleaned_price_str)
                    except InvalidOperation:
                        self.stdout.write(self.style.WARNING(
                            f"Skipping '{product_json_record.get('product_name')}': "
                            f"Invalid price format '{price_string}'"
                        ))
                        continue

                    product_name = product_json_record.get(
                        "product_name"
                    ).strip()

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

                    product_defaults = {
                        "category": product_category,
                    }

                    product_instance, product_created = Product.objects.update_or_create(
                        name=product_name,
                        defaults=product_defaults
                    )

                    product_info_list = product_json_record.get(
                        "product_info", []
                    )

                    product_color = (
                        product_info_list[0] if product_info_list else "N/A"
                    )

                    product_material = self.get_product_material(product_info_list)

                    product_description = "\n".join(product_info_list)

                    ProductDetail.objects.update_or_create(
                        product=product_instance,
                        defaults={
                            "size": DEFAULT_SIZE,
                            "material": product_material,
                            "color": product_color,
                            "stock": DEFAULT_STOCK,
                            "price": product_price,
                            "description": product_description,
                        }
                    )

                    image_url_list = product_json_record.get(
                        "product_images", []
                    )

                    for image_index, image_source_url in enumerate(image_url_list):
                        alt_text = f"{product_name} - Image {image_index + 1}"

                        ProductImage.objects.update_or_create(
                            url=image_source_url,
                            defaults={
                                "product": product_instance,
                                "alt_text": alt_text,
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
