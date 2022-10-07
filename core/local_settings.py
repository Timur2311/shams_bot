
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


ALLOWED_HOSTS = ["*"]
DEBUG = True

# Database configuration
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": "quiz",
#         "USER": "postgres",
#         "PASSWORD": "1111",
#         "HOST": "localhost",
#         "PORT": "5432",
#         "ATOMIC_REQUESTS": True,
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}