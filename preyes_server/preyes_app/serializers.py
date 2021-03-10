from preyes_server.preyes_app.models import Customer
from rest_framework import serializers


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'insertion', 'email', 'notifications', 'birth_date', 'category_preference']