from django.core.management.base import BaseCommand
from master.models import Company


class Command(BaseCommand):
    help = "Load companies from a txt file"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the txt file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        count = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    name = line.strip()

                    if not name:
                        continue

                    obj, created = Company.objects.get_or_create(name=name)

                    if created:
                        count += 1

            self.stdout.write(self.style.SUCCESS(f"Successfully added {count} companies"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {e}"))