import json
from django.core.management.base import BaseCommand
from master.models import City, State, Country


class Command(BaseCommand):
    help = "Load cities from JSON file"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to city JSON file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            count = 0
            for item in data:
                fields = item.get('fields', {})

                # Foreign Keys
                state_obj = State.objects.filter(id=fields.get('state_id')).first()
                country_obj = Country.objects.filter(id=fields.get('country_id')).first()

                City.objects.update_or_create(
                    id=item.get('pk'),
                    defaults={
                        'name': fields.get('name'),
                        'state_id': state_obj,
                        'state_code': fields.get('state_code'),
                        'state_name': fields.get('state_name'),
                        'country_id': country_obj,
                        'country_code': fields.get('country_code'),
                        'country_name': fields.get('country_name'),
                        'latitude': fields.get('latitude'),
                        'longitude': fields.get('longitude'),
                        'wikiDataId': fields.get('wikiDataId'),
                    }
                )
                count += 1

            self.stdout.write(self.style.SUCCESS(f'Successfully loaded {count} cities'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))