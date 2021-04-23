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

    class Meta:
        abstract = True


class Admin(User):

    def __str__(self):
        return "Name: {}".format(self.first_name)

    def get_analytics(self):
        pass


class Customer(User):
    category_preference = models.ManyToManyField('Category')
    auth_user_reference = models.OneToOneField(AuthUser, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return "Email: {}".format(self.email)

    # Delete method is overwritten so that the auth_user linked to the customer is deleted aswell
    def delete(self, *args, **kwargs):
        self.auth_user_reference.delete()
        return super(self.__class__, self).delete(*args, **kwargs)


class RetailerAbstract(models.Model):
    name = models.CharField(max_length=50, null=False)
    base_url = models.CharField(max_length=100, null=False)

    class Meta:
        abstract = True

    def get_categories_retailer(self):
        pass

    def categories_extraction(self, raw_data):
        pass

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
                # TODO: Implement individual monitor for products that are not in the top 100 anymore
                database_product_items = ProductItem.objects.filter(category=category)
                database_product_items_ids = [product.product_id for product in database_product_items]
                all_products = response.json()['products']
                all_products_ids = [product['id'] for product in all_products]
                not_in_top_100 = [value for value in database_product_items_ids if value not in all_products_ids]
                import collections
                for x in [database_item for database_item, count in collections.Counter(database_product_items_ids).items() if count > 1]:
                    ProductItem.objects.filter(product_id=x, category=category)[0].delete()
                for product in all_products:
                    try:
                        product_item = ProductItem.objects.get(product_id=product['id'], category=category)
                        update_values = {
                            "name": product.get('title', 'No title'),
                            "description": product.get('shortDescription', 'No description'),
                            "specs_tag": product.get('specsTag', 'No specsTag'),
                            "product_url": product['urls'][1]['value'] if 'urls' in product.keys() else 'No URLS',
                            "image_url": product['images'][2]['url'] if 'images' in product.keys() else 'No image URL',
                            "price": product['offerData']['offers'][0]['price'],
                            "old_price": product_item.price
                        }
                        for key, value in update_values.items():
                            setattr(product_item, key, value)
                        product_item.save()
                    except ProductItem.DoesNotExist:
                        ProductItem.objects.create(
                            product_id=product['id'],
                            name=product.get('title', 'No title'),
                            retailer_id=retailer,
                            description=product.get('shortDescription', 'No description'),
                            specs_tag=product.get('specsTag', 'No specsTag'),
                            product_url=product['urls'][1]['value'] if 'urls' in product.keys() else 'No URLS',
                            image_url=product['images'][2]['url'] if 'images' in product.keys() else 'No image URL',
                            category=category,
                            product_catalog_reference=catalog,
                            price=product['offerData']['offers'][0]['price'],
                            old_price=product['offerData']['offers'][0]['price']
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
    product_id = models.CharField(max_length=255, null=False, blank=True, default='0')
    old_price = models.DecimalField(null=False, decimal_places=2, max_digits=19, default=0)
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
    target_price = models.DecimalField(null=False, decimal_places=2, max_digits=19, blank=True)
    target_price_type = models.CharField(null=False, choices=(
            ('fixed', 'Fixed'),
            ('percentage', 'Percentage'),
            ('all_discount', 'All Discounts')
        ), max_length=20, default='fixed')
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


class PasswordChangeRequest(models.Model):
    requested_at = models.DateTimeField(auto_now_add=True, null=False)
    email = models.ForeignKey('Customer', on_delete=models.CASCADE, default=None)
    GUID = models.CharField(max_length=250, null=False)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f'Requested at: {self.requested_at} by the user: {self.email}'
