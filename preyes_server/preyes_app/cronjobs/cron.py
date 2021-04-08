from preyes_server.preyes_app.models import *
from preyes_server.preyes_app.notify import notify


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

        # Retrieve the retailer constants for creating or updating objects
        retailer = Retailer.objects.get(name=retailer_object.name)
        catalog = ProductCatalog.objects.get(name='preyes catalog')

        # --------------------------------------------
        # Loop over every category we have
        get_products = getattr(retailer_object, 'get_products')

        result = get_products(all_category_ids, retailer, catalog)
        # --------------------------------------------


def send_notifications_target_items():
    target_items = TargetItem.objects.all()
    for target_item in target_items:
        if target_item.target_price <= target_item.product_item_reference.price:
            customer = Customer.objects.get(id=target_item.target_list_reference.customer_reference_id)
            user_id = customer.auth_user_reference.id
            title = f"{target_item.product_item_reference.name} has met your target price!"
            body = f"Click on the link to buy your wanted product: {target_item.product_item_reference.product_url}"
            notify(user_id, title, body, data=None, sound=True)
