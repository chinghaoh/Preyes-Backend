from django.contrib import admin
from preyes_server.preyes_app import models

admin.site.register(models.Customer)
admin.site.register(models.Admin)
admin.site.register(models.ProductItem)
admin.site.register(models.ProductCatalog)
admin.site.register(models.ProductNotification)
admin.site.register(models.TargetItem)
admin.site.register(models.TargetList)
admin.site.register(models.Retailer)
admin.site.register(models.Category)
admin.site.register(models.PasswordChangeRequest)
