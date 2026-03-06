import json
from django.core.management.base import BaseCommand
from master.models import Country


class Command(BaseCommand):
    help = "Load countries from JSON file into database"

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the country JSON file'
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            count = 0
            for item in data:
                fields = item.get('fields', {})

                Country.objects.update_or_create(
                    id=item.get('pk'),
                    defaults={
                        'name': fields.get('name'),
                        'iso3': fields.get('iso3'),
                        'iso2': fields.get('iso2'),
                        'numeric_code': fields.get('numeric_code'),
                        'phonecode': fields.get('phonecode'),
                        'capital': fields.get('capital'),
                        'currency': fields.get('currency'),
                        'currency_name': fields.get('currency_name'),
                        'currency_symbol': fields.get('currency_symbol'),
                        'tld': fields.get('tld'),
                        'native': fields.get('native'),
                        'region': fields.get('region'),
                        'region_id': fields.get('region_id'),
                        'subregion': fields.get('subregion'),
                        'subregion_id': fields.get('subregion_id'),
                        'nationality': fields.get('nationality'),
                        'latitude': fields.get('latitude'),
                        'longitude': fields.get('longitude'),
                        'emoji': fields.get('emoji'),
                        'emojiU': fields.get('emojiU'),
                        'timezones': fields.get('timezones'),
                        'translations': fields.get('translations'),
                    }
                )
                count += 1

            self.stdout.write(self.style.SUCCESS(f'Successfully loaded {count} countries'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))