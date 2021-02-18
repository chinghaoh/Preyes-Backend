from django.db import models


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

    def get_analytics(self):
        pass


class Customer(User):
    pass


class RetailerAbstract(models.Model):
    name = models.CharField(max_length=50, null=False)
    base_url = models.CharField(max_length=100, null=False)

    class Meta:
        abstract = True

    def get_products(self):
        pass


class Retailer(RetailerAbstract):
    pass


class Product(models.Model):
    name = models.CharField(max_length=100, null=False)

    class Meta:
        abstract = True


class ProductItem(Product):
    retailer_id = models.ForeignKey('Retailer', on_delete=models.CASCADE, default=None)
    price = models.DecimalField(null=False, decimal_places=10, max_digits=19)
    description = models.CharField(max_length=100, null=False, blank=True)
    category = models.CharField(max_length=100, null=False, blank=True)
    product_catalog_reference = models.ForeignKey('ProductCatalog', on_delete=models.CASCADE, default=None)


class ProductCatalog(models.Model):
    pass


class TargetItem(models.Model):
    product_item_reference = models.ForeignKey('ProductItem', on_delete=models.CASCADE, default=None)
    target_price = models.DecimalField(null=False, decimal_places=10, max_digits=19)
    target_list_reference = models.ForeignKey('TargetList', on_delete=models.CASCADE, default=None)


class TargetList(models.Model):
    customer_reference = models.OneToOneField('Customer', on_delete=models.CASCADE, default=None)


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


class Notify(models.Model):
    class Meta:
        abstract = True

    def notify(self):
        pass
