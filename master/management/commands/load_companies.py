import json
from django.core.management.base import BaseCommand
from master.models import Company


class Command(BaseCommand):
    help = "Load companies from JSON file"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to company JSON file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            count = 0
            for item in data:
                fields = item.get('fields', {})

                Company.objects.update_or_create(
                    id=item.get('pk'),
                    defaults={
                        'name': fields.get('name'),
                    }
                )
                count += 1

            self.stdout.write(self.style.SUCCESS(f'Successfully loaded {count} companies'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))