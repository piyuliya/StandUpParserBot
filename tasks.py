from celery import Celery
from celery.schedules import crontab

from parser import check_stand_up_site_page

celery_app = Celery('tasks', broker='redis://localhost:6379/0')


@celery_app.task
def celery_parser():
    check_stand_up_site_page()


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute='*/3'), celery_parser.s())
