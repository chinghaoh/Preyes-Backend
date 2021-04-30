from preyes_server.preyes_app.models import *

from preyes_server.preyes_app.notify import notify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler
trigger_test = CronTrigger.from_crontab('* * * * *')
trigger_categories = CronTrigger.from_crontab('0 1 * * *')
trigger_products = CronTrigger.from_crontab('0 */1 * * *')
trigger_send_notification = CronTrigger.from_crontab('15 */1 * * *')


def test_cron():
    print("I'm working!")


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
        print("Successfully finished CronJob :)")


def send_notifications_target_items():
    target_items = TargetItem.objects.all()

    def calculate_percentage_difference(num1, num2):
        return (abs((num2 - num1)) / num1) * 100

    for target_item in target_items:
        send_notification = False
        product_item = target_item.product_item_reference
        target_price_type = target_item.target_price_type
        if target_price_type == 'fixed' and target_item.target_price <= product_item.price:
            send_notification = True
        elif target_price_type == 'percentage' and calculate_percentage_difference(product_item.price,
                                                                                   product_item.old_price) >= target_item.target_price:
            send_notification = True
        elif target_price_type == 'all_discount' and product_item.price < product_item.old_price:
            send_notification = True
        if send_notification:
            customer = Customer.objects.get(id=target_item.target_list_reference.customer_reference_id)
            user_id = customer.auth_user_reference.id
            title = f"{target_item.product_item_reference.name} has met your target price!"
            body = f"Click on the link to buy your wanted product: {target_item.product_item_reference.product_url}"
            notify(user_id, title, body, data=None, sound=True)


scheduler.add_job(test_cron, trigger_test)
scheduler.add_job(get_categories_retailers, trigger_categories)
scheduler.add_job(get_products_retailers, trigger_products)
scheduler.add_job(send_notifications_target_items, trigger_send_notification)
scheduler.start()
