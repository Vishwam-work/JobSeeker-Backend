import json
from django.core.management.base import BaseCommand
from master.models import JobTitle, JobCategory


class Command(BaseCommand):
    help = "Load job titles from JSON file"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to job title JSON file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            count = 0
            for item in data:
                fields = item.get('fields', {})

                # Get category FK from JSON (category ID)
                category_id = fields.get('category')
                category_obj = JobCategory.objects.filter(id=category_id).first()

                if not category_obj:
                    self.stderr.write(f"Skipping title {fields.get('title')} — category {category_id} not found")
                    continue

                JobTitle.objects.update_or_create(
                    id=item.get('pk'),
                    defaults={
                        'category': category_obj,
                        'title': fields.get('title'),
                    }
                )
                count += 1

            self.stdout.write(self.style.SUCCESS(f"Successfully loaded {count} job titles"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {e}"))