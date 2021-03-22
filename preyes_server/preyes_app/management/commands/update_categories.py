from django.core.management.base import BaseCommand
from preyes_server.preyes_app.models import *


class Command(BaseCommand):
    help = 'Check if update categories works'

    def handle(self, *args, **kwargs):

        retailer_list = [retailer for retailer in RetailerAbstract.__subclasses__() if retailer.__name__ != 'Retailer']
        for retailer in retailer_list:
            retailer_object = retailer()

            # --------------Get retailer api categories--------------
            get_categories_retailer = getattr(retailer_object, 'get_categories_retailer')

            raw_data = get_categories_retailer()
            # ------------------------------

            # Use case 1 - Category does not exist
            # Use case 2 - Category exists, but is not changed from the old value in the DB
            # Use case 3 - Category exist and is different from the old value

            # --------------Retailer api adapter----------------
            categories_extraction = getattr(retailer_object, 'categories_extraction')

            categories = categories_extraction(raw_data)
            # ------------------------------

            # ------------Save categories------------
            for category_id, value in categories.items():
                try:
                    category = Category.objects.get(name=value['name'])
                    if category.category_id != category_id:
                        category.category_id = category_id
                        category.save()

                except Category.DoesNotExist:
                    Category.objects.create(
                        category_id=category_id,
                        name=value['name'],
                        retailer_id=retailer
                    )

            # ------------------------------
