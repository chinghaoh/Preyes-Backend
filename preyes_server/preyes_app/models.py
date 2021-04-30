from django.db import models as django_models
from django.contrib.auth.models import User as AuthUser
import environ
import requests
from django.utils import timezone


# Create your django_models here.
class User(django_models.Model):
    first_name = django_models.CharField(max_length=50, null=False)
    last_name = django_models.CharField(max_length=50, null=False)
    insertion = django_models.CharField(max_length=30, null=True, blank=True)
    email = django_models.EmailField(max_length=100, null=False)
    notifications = django_models.BooleanField(default=False)
    birth_date = django_models.DateField(null=False)

    class Meta:
        abstract = True


class Admin(User):

    def __str__(self):
        return "Name: {}".format(self.first_name)

    def get_analytics(self):
        pass


class Customer(User):
    category_preference = django_models.ManyToManyField('Category')
    auth_user_reference = django_models.OneToOneField(AuthUser, on_delete=django_models.CASCADE, default=None)

    def __str__(self):
        return "Email: {}".format(self.email)

    # Delete method is overwritten so that the auth_user linked to the customer is deleted as well
    def delete(self, *args, **kwargs):
        self.auth_user_reference.delete()
        return super(self.__class__, self).delete(*args, **kwargs)


class RetailerAbstract(django_models.Model):
    name = django_models.CharField(max_length=50, null=False)
    base_url = django_models.CharField(max_length=100, null=False)

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

    def create_or_update_products(self, product, retailer, category, catalog):
        try:
            product_item = ProductItem.objects.get(
                product_id=product['id'], category=category, retailer_id=retailer
            )
            update_values = {
                "name": product.get('title', 'No title'),
                "description": product.get('shortDescription', 'No description'),
                "specs_tag": product.get('specsTag', 'No specsTag'),
                "product_url": product['urls'][1]['value'] if 'urls' in product.keys() else 'No URLS',
                "image_url": product['images'][2]['url'] if 'images' in product.keys() else 'No image URL',
                "price": product['offerData']['offers'][0]['price'] if 'offers' in product[
                    'offerData'] else product_item.price,
                "old_price": product_item.price,
                "last_updated_at": timezone.now(),
                "in_stock": True if 'offers' in product['offerData'] else False
            }
            for key, value in update_values.items():
                setattr(product_item, key, value)
            product_item.save()
        except ProductItem.DoesNotExist:
            try:
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
                    old_price=product['offerData']['offers'][0]['price'],
                    last_updated_at=timezone.now(),
                    in_stock=True if 'offers' in product['offerData'] else False
                )
            except KeyError:
                pass

    def get_products(self, category_ids, retailer, catalog):
        root_dir = environ.Path(__file__) - 3
        env = environ.Env()
        env_file = str(root_dir.path('.env'))
        env.read_env(env_file)
        # This is the request limit for all bol.com request, after the get_product request and
        # the regular get_product requests
        request_limit = 1150
        not_in_top_100 = []
        for category_id in category_ids:
            category = Category.objects.get(category_id=category_id, retailer_id=retailer)
            response = requests.get(
                "{base_url}catalog/v4/lists/?ids={category_id}&apikey={apikey}&dataoutput=products&limit=100".format(
                    base_url=self.base_url,
                    apikey=env('BOL_API_KEY'),
                    category_id=category_id))

            # If the response is OK, create or update the objects
            if response.status_code == 200:
                database_product_items = ProductItem.objects.filter(category=category, retailer_id=retailer)
                database_product_items_ids = [product.product_id for product in database_product_items]
                all_products = response.json()['products']
                all_products_ids = [product['id'] for product in all_products]
                not_in_top_100.extend(
                    [value for value in database_product_items if value.product_id not in all_products_ids])

                import collections
                for x in [database_item for database_item, count in
                          collections.Counter(database_product_items_ids).items() if count > 1]:
                    ProductItem.objects.filter(product_id=x, category=category, retailer_id=retailer)[0].delete()
                for product in all_products:
                    self.create_or_update_products(product, retailer, category, catalog)
        # Sort list ascending with last_updated_at value, to update to products that are not recently updated
        not_in_top_100 = sorted(not_in_top_100, key=lambda product_item: product_item.last_updated_at)
        not_in_top_100 = [product_item.product_id for product_item in not_in_top_100]
        # List with product_ids separated into list of 100, because of product limit of bol.com
        chunks = [','.join(not_in_top_100[x:x + 100]) for x in range(0, len(not_in_top_100), 100)]
        if len(chunks) > request_limit:
            chunks = chunks[:request_limit + 1]
        for chunk in chunks:
            request_url = f"{self.base_url}catalog/v4/products/{chunk}?limit=100&apikey={env('BOL_API_KEY')}&format=json"
            response = requests.get(url=request_url)
            if response.status_code == 200:
                chunk_products = response.json()['products']
                for chunk_product in chunk_products:
                    try:
                        remote_category = chunk_product['parentCategoryPaths'][0]['parentCategories'][0]['id']
                        database_category = Category.objects.get(category_id=remote_category, retailer_id=retailer)
                    except KeyError as e:
                        print(f"An error occurred for {chunk_product['id']}: {e}")
                        continue
                    except IndexError as e:
                        print(f"An error occurred for {chunk_product['id']}: {e}")
                        continue
                    except Category.DoesNotExist:
                        print(f"No category found for product not in top 100: {chunk_product['id']}")
                        continue
                    self.create_or_update_products(
                        product=chunk_product,
                        retailer=retailer,
                        category=database_category,
                        catalog=catalog
                    )


class Retailer(RetailerAbstract):
    pass

    def __str__(self):
        return "Retailer: {}".format(self.name)


class Product(django_models.Model):
    name = django_models.TextField(null=False)

    class Meta:
        abstract = True


class ProductItem(Product):
    retailer_id = django_models.ForeignKey('Retailer', on_delete=django_models.CASCADE, default=None)
    price = django_models.DecimalField(null=False, decimal_places=2, max_digits=19)
    product_id = django_models.CharField(max_length=255, null=False, blank=True, default='0')
    old_price = django_models.DecimalField(null=False, decimal_places=2, max_digits=19, default=0)
    description = django_models.TextField(null=False, blank=True)
    specs_tag = django_models.TextField(null=False, blank=True)
    product_url = django_models.URLField(max_length=2048, null=False, blank=True)
    image_url = django_models.URLField(max_length=2048, null=False, blank=True)
    category = django_models.ForeignKey('Category', on_delete=django_models.SET_NULL, default=None, null=True)
    product_catalog_reference = django_models.ForeignKey('ProductCatalog', on_delete=django_models.CASCADE, default=None)
    last_updated_at = django_models.DateTimeField(null=False, default=timezone.now)
    in_stock = django_models.BooleanField(null=False, default=True)

    def __str__(self):
        return "Product: {} Retailer: {}".format(self.name, self.retailer_id.name)


class ProductCatalog(django_models.Model):
    name = django_models.CharField(max_length=100, default="preyes catalog")
    pass

    def __str__(self):
        return "Name: {}".format(self.name)


class TargetItem(django_models.Model):
    product_item_reference = django_models.ForeignKey('ProductItem', on_delete=django_models.CASCADE, default=None)
    target_price = django_models.DecimalField(null=False, decimal_places=2, max_digits=19, blank=True)
    target_price_type = django_models.CharField(null=False, choices=(
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage'),
        ('all_discount', 'All Discounts')
    ), max_length=20, default='fixed')
    target_list_reference = django_models.ForeignKey('TargetList', on_delete=django_models.CASCADE, default=None)

    def __str__(self):
        return "Product: {} Email: {}".format(self.product_item_reference.name,
                                              self.target_list_reference.customer_reference.email)


class TargetList(django_models.Model):
    customer_reference = django_models.OneToOneField('Customer', on_delete=django_models.CASCADE, default=None)

    def __str__(self):
        return "Email: {}".format(self.customer_reference.email)


class Notification(django_models.Model):
    message = django_models.CharField(max_length=250, null=False)
    date = django_models.DateField(null=False)
    time_stamp = django_models.DateTimeField(null=False)

    class Meta:
        abstract = True


class ProductNotification(Notification):
    target_item = django_models.OneToOneField(
        'TargetItem',
        on_delete=django_models.CASCADE,
    )

    def __str__(self):
        return "Product name: {} User: {}".format(self.target_item.product_item_reference.name,
                                                  self.target_item.target_list_reference.customer_reference.email)


class Notify(django_models.Model):
    class Meta:
        abstract = True

    def notify(self):
        pass


class Category(django_models.Model):
    category_id = django_models.CharField(max_length=250, null=False, default=0, primary_key=True)
    name = django_models.CharField(max_length=250, null=False)
    retailer_id = django_models.ForeignKey('Retailer', on_delete=django_models.CASCADE, default=None)

    def __str__(self):
        return "Category name: {}".format(self.name)


class PasswordChangeRequest(django_models.Model):
    requested_at = django_models.DateTimeField(auto_now_add=True, null=False)
    email = django_models.ForeignKey('Customer', on_delete=django_models.CASCADE, default=None)
    GUID = django_models.CharField(max_length=250, null=False)
    used = django_models.BooleanField(default=False)

    def __str__(self):
        return f'Requested at: {self.requested_at} by the user: {self.email}'
