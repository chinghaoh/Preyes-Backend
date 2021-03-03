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

    def __str__(self):
        return "Name: {}".format(self.first_name)

    def get_analytics(self):
        pass


class Customer(User):

    def __str__(self):
        return "Email: {}".format(self.email)

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
    target_price = models.DecimalField(null=False, decimal_places=10, max_digits=19)
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
