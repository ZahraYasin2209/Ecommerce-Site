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


CATEGORY_MAPPING = {
    'PESHAWARI CHAPPAL': 'Peshawari Chappal',
    'KAMEEZ SHALWAR': 'Kameez Shalwar',
    'WAISTCOAT': 'Waistcoat',
    'SANDALS': 'Sandals',
    'KURTI': 'Kurti',
    'KURTA': 'Kurta',
    'CAP': 'Cap',
}


class Command(BaseCommand):
    help = 'Loads product data from clothes.json and stores them in respective models in database.'

    def handle(self, *args, **options):
        try:
            from django.apps import apps

            products_app_config = apps.get_app_config('products')
            app_directory = products_app_config.path
        except LookupError:
            raise CommandError(
                "Could not find the 'products' app configuration."
            )

        json_file_path = os.path.join(app_directory, 'clothes.json')

        if not os.path.exists(json_file_path):
            raise CommandError(
                f'File not found at: {json_file_path}. '
                f'Please ensure "clothes.json" is in the root of the products app directory.')

        self.stdout.write(f"Starting product data import from {json_file_path}")

        try:
            with open(json_file_path, 'r', encoding='utf-8') as json_file:
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
                        'product_price', '0.00'
                    )

                    cleaned_price_str = (
                        price_string
                        .replace('PKR\xa0', '')
                        .replace('PKR ', '')
                        .replace(',', '')
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
                        'product_name'
                    ).strip()

                    category_name = 'Others'

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
                        'category': product_category,
                    }

                    product_instance, product_created = Product.objects.update_or_create(
                        name=product_name,
                        defaults=product_defaults
                    )

                    product_info_list = product_json_record.get(
                        'product_info', []
                    )

                    product_color = (
                        product_info_list[0] if product_info_list else 'N/A'
                    )

                    product_material = 'N/A'
                    for info_item in product_info_list:
                        if 'Cotton' in info_item:
                            product_material = 'Cotton'
                            break
                        elif 'Blended' in info_item:
                            product_material = 'Blended'
                            break

                    product_description = "\n".join(product_info_list)

                    ProductDetail.objects.update_or_create(
                        product=product_instance,
                        defaults={
                            'size': SizeChoices.M,
                            'material': product_material,
                            'color': product_color,
                            'stock': 1,
                            'price': product_price,
                            'description': product_description,
                        }
                    )

                    image_url_list = product_json_record.get(
                        'product_images', []
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
                        f"{product_json_record.get('product_name', 'N/A')}. "
                        f"Error: {error}"
                    ))

        self.stdout.write("\n")
        self.stdout.write(self.style.SUCCESS(
            f"Successfully imported {success_imports_counter}/{total_products_present} products."
        ))
