from django.core.management.base import BaseCommand
from preyes_server.preyes_app.models import *


class Command(BaseCommand):
    help = 'Run this command to retrieve the 100 most popular products from each category, from Bol.com API'

    def handle(self, *args, **kwargs):
        # ----------------------------------------
        # Retrieve all the category id's
        all_category_ids = [x.category_id for x in Category.objects.all() if x.category_id != '0']
        retailer_list = [retailer for retailer in RetailerAbstract.__subclasses__() if
                         retailer.__name__ != 'Retailer']

        for retailer_class in retailer_list:
            retailer_object = retailer_class()

            # --------------------------------------------

            # Retrieve retailer constants for creating or updating objects
            retailer = Retailer.objects.get(name=retailer_object.name)
            catalog = ProductCatalog.objects.get(name='preyes catalog')

            # --------------------------------------------
            # Loop over every category we have
            get_products = getattr(retailer_object, 'get_products')

            result = get_products(all_category_ids, retailer, catalog)
            # --------------------------------------------
