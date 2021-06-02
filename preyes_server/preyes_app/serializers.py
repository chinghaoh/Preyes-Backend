from preyes_server.preyes_app.models import Customer, ProductItem, Category, TargetItem, TargetList
from rest_framework import serializers


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'insertion', 'email', 'notifications', 'birth_date',
                  'category_preference', 'auth_user_reference']


class ProductItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductItem
        fields = [
            'id', 'retailer_id', 'price', 'old_price', 'description', 'specs_tag', 'product_url',
            'image_url', 'category', 'product_catalog_reference', 'name', 'in_stock'
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'name', 'retailer_id']


class TargetItemSerializer(serializers.ModelSerializer):
    product_item_reference = ProductItemSerializer(read_only=True)

    class Meta:
        model = TargetItem
        fields = ['product_item_reference', 'target_price', 'target_price_type', 'target_list_reference']


class TargetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TargetList
        fields = ['customer_reference']
