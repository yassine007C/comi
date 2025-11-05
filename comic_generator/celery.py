# myproject/celery.py

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')

# Redis URL or your Redis’s connection string
app.conf.broker_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
