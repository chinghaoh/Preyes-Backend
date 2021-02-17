from django.db import models


# Create your models here.
class User(models.Model):
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False)
    insertion = models.CharField(max_length=30, null=True, blank=True)
    email = models.CharField(max_length=100, null=False)
    notifications = models.BooleanField(default=False)
    birth_date = models.DateField(null=False)

    class Meta:
        abstract = True


class Admin(User):

    def get_analytics(self):
        pass


class Customer(User):
    pass
