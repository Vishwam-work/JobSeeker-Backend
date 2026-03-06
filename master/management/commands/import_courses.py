from django.core.management.base import BaseCommand
from master.models import CourseMaster

class Command(BaseCommand):
    help = "Import courses from course.txt"

    def handle(self, *args, **kwargs):
        file_path = "D:\Vishwam Program\project\Backend\Jobseeker\master\management\commands\course.txt"

        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                course_name = line.strip()

                if course_name:
                    CourseMaster.objects.get_or_create(name=course_name)

        self.stdout.write(self.style.SUCCESS("Courses imported successfully"))