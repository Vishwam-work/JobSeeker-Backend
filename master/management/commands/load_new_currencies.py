import json
from django.core.management.base import BaseCommand
from master.models import Currency


class Command(BaseCommand):
    help = "Import currencies from JSON"

    def handle(self, *args, **kwargs):
        with open("./master/management/commands/currencies.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        for key, value in data.items():
            Currency.objects.update_or_create(
                code=value["code"],
                defaults={
                    "name": value["name"],
                    "symbol": value["symbol"],
                    "symbol_native": value.get("symbolNative")
                }
            )

        self.stdout.write(self.style.SUCCESS("Currencies imported successfully"))