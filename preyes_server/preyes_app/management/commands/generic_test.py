from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Try out test code snippets here'

    def handle(self, *args, **kwargs):
        pass
