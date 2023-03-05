from celery import periodic_task
from celery import crontab
from django.db.models import F, ExpressionWrapper, BooleanField
from .models import Link
import datetime


@periodic_task(run_every=crontab(seconds='*/30'))
def make_expired():
    now = datetime.datetime.now()
    Link.objects.annotate(is_expired=ExpressionWrapper(
        F('expiration_date') < now, 
        output_field=BooleanField(),
    ))

@periodic_task(run_every=crontab(hour='*/12'))
def delete_expired():
    links = Link.objects.filter(is_expired=True)
    links.delete()