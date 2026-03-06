import json
from django.core.management.base import BaseCommand
from master.models import State, Country


class Command(BaseCommand):
    help = "Load states from JSON file"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to state JSON file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            count = 0
            for item in data:
                fields = item.get('fields', {})

                country_id = fields.get('country_id')

                country_obj = Country.objects.filter(id=country_id).first()

                State.objects.update_or_create(
                    id=item.get('pk'),
                    defaults={
                        'name': fields.get('name'),
                        'country_id': country_obj,
                        'country_name': fields.get('country_name'),
                        'country_code': fields.get('country_code'),
                        'state_code': fields.get('state_code'),
                        'type': fields.get('type'),
                        'latitude': fields.get('latitude'),
                        'longitude': fields.get('longitude'),
                    }
                )
                count += 1

            self.stdout.write(self.style.SUCCESS(f'Successfully loaded {count} states'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))