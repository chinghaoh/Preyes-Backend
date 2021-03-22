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

def proces_products_bol():
    # Set up env file for getting secret keys
    root_dir = environ.Path(__file__) - 4
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
                    product_url=product['urls'][1]['value'] if 'urls' in product.keys() else 'No URLS',
                    image_url=product['images'][2]['url'] if 'images' in product.keys() else 'No image URL',
                    category=category,
                    product_catalog_reference=catalog,
                    defaults={'price': product['offerData']['offers'][0]['price']}
                )
