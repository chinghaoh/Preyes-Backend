from django.core.management.base import BaseCommand
import environ
import requests
from preyes_server.preyes_app.models import Category, Retailer, ProductItem, ProductCatalog


class Command(BaseCommand):
    help = 'Run this command to retrieve the 100 most popular products from each category, from Bol.com API'

    def handle(self, *args, **kwargs):
        # Set up env file for getting secret keys
        root_dir = environ.Path(__file__) - 5
        env = environ.Env()
        env_file = str(root_dir.path('.env'))
        env.read_env(env_file)

        # Retrieve all the category id's
        all_category_ids = [x.category_id for x in Category.objects.all() if x.category_id != '0']

        # Set up request
        base_url = 'https://api.bol.com/catalog/v4/'
        api_key = env('BOL_API_KEY')

        # Retrieve the bol.com constants for creating or updating objects
        retailer = Retailer.objects.get(name='bol.com')
        catalog = ProductCatalog.objects.get(name='preyes catalog')

        # Loop over every category we have
        for category_id in all_category_ids:
            category = Category.objects.get(category_id=category_id)
            response = requests.get(
                "{base_url}/lists/?ids={category_id}&apikey={apikey}&dataoutput=products&limit=100".format(
                    base_url=base_url,
                    apikey=api_key,
                    category_id=category_id))

            # If the response is OK, create or update the objects
            if response.status_code == 200:
                all_products = response.json()['products']
                for product in all_products:
                    new_product = ProductItem.objects.update_or_create(
                        name=product.get('title', 'No title'),
                        retailer_id=retailer,
                        description=product.get('shortDescription', 'No description'),
                        specs_tag=product.get('specsTag', 'No specsTag'),
                        product_url=product['urls'][1]['value'],
                        image_url=product['images'][2]['url'],
                        category=category,
                        product_catalog_reference=catalog,
                        defaults={'price': product['offerData']['offers'][0]['price']}
                    )