ALLOWED_HOSTS = ["*"]
DEBUG = True

# Database configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "quiz",
        "USER": "postgres",
        "PASSWORD": "1111",
        "HOST": "localhost",
        "PORT": "5432",
        "ATOMIC_REQUESTS": True,
    }
}
