from django.core.management.base import BaseCommand
from preyes_server.preyes_app.notify import notify


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        return notify(**kwargs)
