import os

from celery import Celery


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangelery.settings')

app = Celery('djangelery')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'test-message': {
        'task': 'ctasks.tasks.ctasks_demo',
        'schedule': 5.0,
        'args': ('FUCK THIS SHIT!!!',)
    }
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


@app.task
def test_task(self):
    print(f'Suck my dick!')
    return 'Ma\' dick'
