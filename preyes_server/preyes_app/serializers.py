from preyes_server.preyes_app.models import Customer, ProductItem, Category
from rest_framework import serializers


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'insertion', 'email', 'notifications', 'birth_date', 'category_preference']


class ProductItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductItem
        fields = [
            'id', 'retailer_id', 'price', 'description', 'specs_tag', 'product_url',
            'image_url', 'category', 'product_catalog_reference'
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'name', 'retailer_id']
