import requests
import environ
from preyes_server.preyes_app.models import Category, Retailer


def get_categories_bol():
    root_dir = environ.Path(__file__) - 4
    env = environ.Env()
    env_file = str(root_dir.path('.env'))
    env.read_env(env_file)

    base_url = 'https://api.bol.com/catalog/v4/'
    response = requests.get(
        "{base_url}/lists/?ids=0&apikey={apikey}&dataoutput=categories".format(base_url=base_url,
                                                                               apikey=env('BOL_API_KEY'))).json()

    # Use case 1 - Category does not exist
    # Use case 2 - Category exists, but is not changed from the old value in the DB
    # Use case 3 - Category exist and is different from the old value

    categories = {
        response['originalRequest']['category']['id']: {
            'name': response['originalRequest']['category']['name']
        }
    }

    for category in response['categories']:
        categories[category['id']] = {
            'name': category['name']
        }
    retailer = Retailer.objects.get(name='bol.com')
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
                retailer_id__id=retailer
            )
