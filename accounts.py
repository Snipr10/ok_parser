from django.db.models import Q

from core.models import Sessions
from django.utils import timezone
from datetime import timedelta
import time


def update_time_timezone(my_time):
    return my_time + timedelta(hours=3)


def get_new_session():
    s = Sessions.objects.filter(Q(last_parsing__isnull=True) | Q(last_parsing__lte=update_time_timezone(
        timezone.localtime()) - timedelta(minutes=5)), is_parsing=False, is_active__lte=100, proxy_id__isnull=False
                                   ).order_by('last_parsing').first()
    s.is_parsing=True
    s.save(update_fields=["is_parsing"])
    return s


def get_session_update(session):
    now = update_time_timezone(timezone.localtime())
    session.is_parsing = True
    session.start_parsing = now
    session.last_parsing = now
    session.save(update_fields=['is_parsing', 'start_parsing', 'last_parsing'])


def stop_session(session, attempt=0):
    try:
        session.is_parsing = 0
        session.last_parsing = update_time_timezone(timezone.now())
        session.save(update_fields=['is_parsing', 'last_parsing'])
    except Exception as e:
        print(e)
        attempt += 1
        if attempt < 6:
            time.sleep(5)
            stop_session(session, attempt=attempt)


def stop_source(sources_item, attempt=0):
    try:
        sources_item.taken = 0
        sources_item.save(update_fields=['taken'])
    except Exception as e:
        print(e)
        attempt += 1
        if attempt < 6:
            time.sleep(5)
            stop_source(sources_item, attempt=attempt)
