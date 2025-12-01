import json
import os
from decimal import Decimal, InvalidOperation

from django.core.management.base import (
    BaseCommand, CommandError
)
from django.db import transaction

from products.choices import SizeChoices
from products.models import (
    Category, Product, ProductDetail, ProductImage
)
from .mappings import CATEGORY_MAPPING


class Command(BaseCommand):
    help = "Loads product data from clothes.json and stores them in respective models in database."

    def handle(self, *args, **options):
        command_dir = os.path.dirname(os.path.abspath(__file__))

        data_dir = os.path.join(os.path.dirname(command_dir), 'data')
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

        total_products_present = len(product_data_list)
        success_imports_counter = 0

        with transaction.atomic():
            for product_json_record in product_data_list:
                try:
                    price_string = product_json_record.get(
                        "product_price", "0.00"
                    )

                    cleaned_price_str = (
                        price_string
                        .replace("PKR\xa0", "")
                        .replace("PKR ", "")
                        .replace(",", "")
                        .strip()
                    )

                    try:
                        product_price = Decimal(cleaned_price_str)
                    except InvalidOperation:
                        self.stdout.write(self.style.WARNING(
                            f"Skipping '{product_json_record.get("product_name")}': "
                            f"Invalid price format '{price_string}'"
                        ))
                        continue

                    product_name = product_json_record.get(
                        "product_name"
                    ).strip()

                    assigned_category_name = "Others"

                    for category_identifier, finalized_category_name in CATEGORY_MAPPING.items():
                        if category_identifier in product_name.upper():
                            assigned_category_name = finalized_category_name
                            break

                    product_category, category_created = Category.objects.get_or_create(
                        name=assigned_category_name
                    )

                    if category_created:
                        self.stdout.write(self.style.SUCCESS(
                            f" Created new Category: {assigned_category_name}"
                        ))

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

                    product_material = "N/A"
                    for info_item in product_info_list:
                        if "Cotton" in info_item:
                            product_material = "Cotton"
                            break
                        elif "Blended" in info_item:
                            product_material = "Blended"
                            break

                    product_description = "\n".join(product_info_list)

                    ProductDetail.objects.update_or_create(
                        product=product_instance,
                        defaults={
                            "size": SizeChoices.M,
                            "material": product_material,
                            "color": product_color,
                            "stock": 1,
                            "price": product_price,
                            "description": product_description,
                        }
                    )

                    image_url_list = product_json_record.get(
                        "product_images", []
                    )

                    for image_index, image_source_url in enumerate(image_url_list):
                        pass

                    success_imports_counter += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"  [SUCCESS] Product: {product_name} ({product_category.name})"
                    ))

                except Exception as error:
                    self.stdout.write(self.style.ERROR(
                        f"Failed to process product: "
                        f"{product_json_record.get("product_name", "N/A")}. "
                        f"Error: {error}"
                    ))

        self.stdout.write("\n")
        self.stdout.write(self.style.SUCCESS(
            f"Successfully imported {success_imports_counter}/{total_products_present} products."
        ))
