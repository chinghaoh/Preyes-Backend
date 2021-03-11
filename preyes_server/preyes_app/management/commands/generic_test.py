from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from preyes_server.preyes_app.models import Customer


class Command(BaseCommand):
    help = 'Try out test code snippets here'

    def handle(self, *args, **kwargs):
        customer = Customer.objects.get(email="Testing@tester.com")
