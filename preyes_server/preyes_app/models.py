from django.db import models
from django.contrib.auth.models import User as AuthUser
import environ
import requests


# Create your models here.
class User(models.Model):
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False)
    insertion = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(max_length=100, null=False)
    notifications = models.BooleanField(default=False)
    birth_date = models.DateField(null=False)
    auth_user_reference = models.OneToOneField(AuthUser, on_delete=models.CASCADE, default=None)

    class Meta:
        abstract = True


class Admin(User):

    def __str__(self):
        return "Name: {}".format(self.first_name)

    def get_analytics(self):
        pass


class Customer(User):
    category_preference = models.ManyToManyField('Category')

    def __str__(self):
        return "Email: {}".format(self.email)

    pass


class RetailerAbstract(models.Model):
    name = models.CharField(max_length=50, null=False)
    base_url = models.CharField(max_length=100, null=False)

    class Meta:
        abstract = True

    def get_products(self, category_ids, retailer, catalog):
        pass


class Bol(RetailerAbstract):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'bol.com'
        self.base_url = 'https://api.bol.com/'

    # Method to gather the categories of a retailer
    def get_categories_retailer(self):
        root_dir = environ.Path(__file__) - 3
        env = environ.Env()
        env_file = str(root_dir.path('.env'))
        env.read_env(env_file)

        url = "{base_url}catalog/v4/lists/?ids=0&apikey={apikey}&dataoutput=categories".format(
            base_url=self.base_url, apikey=env('BOL_API_KEY'))

        response = None
        try:
            response = requests.get(url).json()
        except Exception as e:
            print(f'Error occurred: {e}')

        return response

    # Method to extract categories from raw_data of retailer request
    def categories_extraction(self, raw_data):
        categories = None
        try:

            categories = {
                raw_data['originalRequest']['category']['id']: {
                    'name': raw_data['originalRequest']['category']['name']
                }
            }

            for category in raw_data['categories']:
                categories[category['id']] = {
                    'name': category['name']
                }
        except KeyError:
            print(f'Error occurred when trying to access a key from raw_data')

        except Exception as e:
            print(f'Error occurred: {e}')

        return categories

    def get_products(self, category_ids, retailer, catalog):
        root_dir = environ.Path(__file__) - 3
        env = environ.Env()
        env_file = str(root_dir.path('.env'))
        env.read_env(env_file)

        for category_id in category_ids:
            category = Category.objects.get(category_id=category_id, retailer_id=retailer)
            response = requests.get(
                "{base_url}catalog/v4/lists/?ids={category_id}&apikey={apikey}&dataoutput=products&limit=100".format(
                    base_url=self.base_url,
                    apikey=env('BOL_API_KEY'),
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


class Retailer(RetailerAbstract):
    pass

    def __str__(self):
        return "Retailer: {}".format(self.name)


class Product(models.Model):
    name = models.TextField(null=False)

    class Meta:
        abstract = True


class ProductItem(Product):
    retailer_id = models.ForeignKey('Retailer', on_delete=models.CASCADE, default=None)
    price = models.DecimalField(null=False, decimal_places=2, max_digits=19)
    description = models.TextField(null=False, blank=True)
    specs_tag = models.TextField(null=False, blank=True)
    product_url = models.URLField(max_length=2048, null=False, blank=True)
    image_url = models.URLField(max_length=2048, null=False, blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, default=None, null=True)
    product_catalog_reference = models.ForeignKey('ProductCatalog', on_delete=models.CASCADE, default=None)

    def __str__(self):
        return "Product: {} Retailer: {}".format(self.name, self.retailer_id.name)


class ProductCatalog(models.Model):
    name = models.CharField(max_length=100, default="preyes catalog")
    pass

    def __str__(self):
        return "Name: {}".format(self.name)


class TargetItem(models.Model):
    product_item_reference = models.ForeignKey('ProductItem', on_delete=models.CASCADE, default=None)
    target_price = models.DecimalField(null=False, decimal_places=2, max_digits=19)
    target_list_reference = models.ForeignKey('TargetList', on_delete=models.CASCADE, default=None)

    def __str__(self):
        return "Product: {} Email: {}".format(self.product_item_reference.name,
                                              self.target_list_reference.customer_reference.email)


class TargetList(models.Model):
    customer_reference = models.OneToOneField('Customer', on_delete=models.CASCADE, default=None)

    def __str__(self):
        return "Email: {}".format(self.customer_reference.email)


class Notification(models.Model):
    message = models.CharField(max_length=250, null=False)
    date = models.DateField(null=False)
    time_stamp = models.DateTimeField(null=False)

    class Meta:
        abstract = True


class ProductNotification(Notification):
    target_item = models.OneToOneField(
        'TargetItem',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "Product name: {} User: {}".format(self.target_item.product_item_reference.name,
                                                  self.target_item.target_list_reference.customer_reference.email)


class Notify(models.Model):
    class Meta:
        abstract = True

    def notify(self):
        pass


class Category(models.Model):
    category_id = models.CharField(max_length=250, null=False, default=0, primary_key=True)
    name = models.CharField(max_length=250, null=False)
    retailer_id = models.ForeignKey('Retailer', on_delete=models.CASCADE, default=None)

    def __str__(self):
        return "Category name: {}".format(self.name)
