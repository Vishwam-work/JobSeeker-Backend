from django.core.management.base import BaseCommand
from master.models import JobCategory


class Command(BaseCommand):
    help = "Load predefined job categories"

    def handle(self, *args, **kwargs):
        categories = [
            "Startups",
            "Product Management",
            "Finance & Accounting",
            "Sales & Business Development",
            "Human Resources",
            "Marketing",
            "Public Relations",
            "Design",
            "Data Science",
            "Mobile Development",
            "Web Development"
        ]

        count = 0
        for name in categories:
            obj, created = JobCategory.objects.get_or_create(name=name)
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully added {count} categories"))