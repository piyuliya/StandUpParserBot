from celery import Celery
from celery.schedules import crontab

from parser import check_stand_up_site_page
from update_avalability import check_update_availability
from update_url import check_update_url


celery_app = Celery('tasks', broker='redis://localhost:6379/0')


@celery_app.task
def celery_parser():
    check_stand_up_site_page()


@celery_app.task
def celery_update_ulr():
    check_update_url()


@celery_app.task
def celery_update_avalability():
    check_update_availability()


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute='*/5'), celery_parser.s())
    sender.add_periodic_task(crontab(minute='*/5'), celery_update_ulr.s())
    sender.add_periodic_task(crontab(minute='*/3'), celery_update_avalability.s())
