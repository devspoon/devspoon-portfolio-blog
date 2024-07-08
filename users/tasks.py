from __future__ import absolute_import, unicode_literals
import logging

from django.conf import settings
from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from users.models import User

from time import sleep

logger = logging.getLogger(getattr(settings, "CELERY_LOGGER", "django"))


@shared_task
def delete_users_with_unverified_emails():
    logger.debug("delete_users_with_unverified_emails start")
    three_days_ago = timezone.now() - timezone.timedelta(days=3)
    result = User.objects.filter(created_at__lte=three_days_ago, verified=False)
    cnt = result.count()
    logger.debug("Number of emails that need to be deleted : ", extra={"count:": cnt})
    result.delete()
    return cnt
