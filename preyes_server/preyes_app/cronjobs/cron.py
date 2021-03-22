from preyes_server.preyes_app.models import *


def get_categories_retailers():
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


def get_products_retailers():
    # ----------------------------------------
    # Retrieve all the category id's
    all_category_ids = [x.category_id for x in Category.objects.all() if x.category_id != '0']
    retailer_list = [retailer for retailer in RetailerAbstract.__subclasses__() if
                     retailer.__name__ != 'Retailer']

    for retailer_class in retailer_list:
        retailer_object = retailer_class()

        # --------------------------------------------

        # Retrieve the bol.com constants for creating or updating objects
        retailer = Retailer.objects.get(name=retailer_object.name)
        catalog = ProductCatalog.objects.get(name='preyes catalog')

        # --------------------------------------------
        # Loop over every category we have
        get_products = getattr(retailer_object, 'get_products')

        result = get_products(all_category_ids, retailer, catalog)
        # --------------------------------------------
