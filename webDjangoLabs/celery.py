import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webDjangoLabs.settings')

app = Celery('webDjangoLabs',)

app.conf.broker_url = 'redis://127.0.0.1:6379/0'

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
