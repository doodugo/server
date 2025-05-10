import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
celery_broker_url = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
celery_result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

app = Celery("core")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.broker_url = celery_broker_url
app.conf.result_backend = celery_result_backend

app.autodiscover_tasks()
