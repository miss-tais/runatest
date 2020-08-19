from .base import *  # noqa

DEBUG = True

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", default="!!!SET DJANGO_SECRET_KEY!!!")

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]
