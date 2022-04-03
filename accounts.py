from django.db.models import Q

from core.models import Sessions
from django.utils import timezone
from datetime import timedelta


def update_time_timezone(my_time):
    return my_time + timedelta(hours=3)


def get_new_session():
    return Sessions.objects.filter(Q(last_parsing__isnull=True) | Q(last_parsing__lte=update_time_timezone(
        timezone.localtime()) - timedelta(minutes=5)), is_parsing=False, is_active__lte=10, proxy_id__isnull=False
                                   ).order_by('last_parsing').first()

def get_session_update(session):
    now = update_time_timezone(timezone.localtime())
    session.is_parsing = True
    session.start_parsing = now
    session.last_parsing = now
    session.save(update_fields=['is_parsing', 'start_parsing', 'last_parsing'])