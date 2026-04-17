import sys
from pathlib import Path
from .base import *

DEBUG = True
CORS_ALLOW_ALL_ORIGINS = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

if getattr(sys, "frozen", False):
    ML_WEIGHTS_DIR = Path(sys._MEIPASS) / "ml" / "weights"
    DATABASES["default"]["NAME"] = Path.home() / ".confmaster" / "db.sqlite3"
    Path.home().joinpath(".confmaster").mkdir(parents=True, exist_ok=True)

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_RESULT_BACKEND = "django-db"
