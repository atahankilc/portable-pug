import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core_api.settings.local")

from django.core.management import execute_from_command_line

execute_from_command_line(["manage.py", "runserver", "127.0.0.1:8000", "--noreload"])
