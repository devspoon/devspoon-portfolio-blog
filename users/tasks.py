from __future__ import absolute_import, unicode_literals

from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from users.models import User

from time import sleep


@shared_task
def delete_users_with_unverified_emails():
    print("delete_users_with_unverified_emails start")
    three_days_ago = timezone.now() - timezone.timedelta(days=3)
    result = User.objects.filter(created_at__lte=three_days_ago, verified=False)
    cnt = result.count()
    print("cnt : ", cnt)
    result.delete()
    return cnt
