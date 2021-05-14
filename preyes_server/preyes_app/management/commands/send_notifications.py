from django.core.management.base import BaseCommand

from preyes_server.preyes_app.models import TargetItem, Customer
from preyes_server.preyes_app.notify import notify


class Command(BaseCommand):
    help = 'Check if update categories works'

    def handle(self, *args, **kwargs):
        target_items = TargetItem.objects.all()

        def calculate_percentage_difference(num1, num2):
            return (abs((num2 - num1)) / num1) * 100

        for target_item in target_items:
            send_notification = False
            product_item = target_item.product_item_reference
            target_price_type = target_item.target_price_type
            if target_price_type == 'fixed' and target_item.target_price >= product_item.price:
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
