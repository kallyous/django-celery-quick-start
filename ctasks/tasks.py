# Create your tasks here

from celery import shared_task


@shared_task
def ctasks_demo(msg):
    return msg


@shared_task
def add(x, y):
    return x + y
