#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import time

import django.db
import threading
import random
import multiprocessing

import requests


def new_process_source(i):
    for i in range(1):
        time.sleep(random.randint(1, 5))
        print(f"multiprocessing source {i}")
        x = threading.Thread(target=start_task_while_source, args=(i,))
        x.start()


def start_task_while_source(i):
    null_result = 0
    while True:
        try:
            django.db.close_old_connections()
            result_count = start_task_source()
            if result_count == 0:
                null_result += 1
        except Exception as e:
            null_result += 1
            time.sleep(random.randint(5, 10))
            print(e)
        if null_result >= 100:
            raise Exception("null count > 100")


def start_task_source():
    result_count = 0
    from django.db.models import Q

    from core.models import Sources
    from django.utils import timezone
    from accounts import get_new_session
    from accounts import update_time_timezone
    from accounts import stop_session
    from accounts import stop_source
    from saver import save_result
    from core.models import SourcesItems
    import datetime

    session = None
    sources_item = None
    try:
        django.db.close_old_connections()
        session = get_new_session()
        print(f"session is  {session}")

        if session:
            now = update_time_timezone(timezone.localtime())
            session.is_parsing = True
            session.start_parsing = now
            session.last_parsing = now
            session.save(update_fields=['is_parsing', 'start_parsing', 'last_parsing'])
        else:
            time.sleep(random.randint(100, 150))
            return
        print(f"start")
        select_sources = Sources.objects.filter(
            Q(retro_max__isnull=True) | Q(retro_max__gte=timezone.now()), published=1,
            status=1)
        sources_item = SourcesItems.objects.filter(network_id=10, disabled=0, taken=0,
                                                   source_id__in=list(select_sources.values_list('id', flat=True))) \
            .order_by('last_modified').first()
        print(sources_item.id)
        # time = select_sources.get(id=sources_item.source_id).sources
        print(1)
        result = []
        if sources_item is not None:
            time_s = select_sources.get(id=sources_item.source_id).sources
            if time_s is None:
                time_s = 0
            print(2)

            if sources_item.last_modified is None or (
                    sources_item.last_modified + datetime.timedelta(minutes=time_s) <
                    update_time_timezone(timezone.localtime())):
                sources_item.taken = 1
                sources_item.save()
                print(3)

                if sources_item.type == 22:
                    if "group/" in sources_item.data:
                        sources_item.type = 20
                    elif "profile/" in sources_item.data:
                        sources_item.type = 21
                    else:
                        type_ = check_user_group(sources_item, session)
                        if type_:
                            sources_item.type = type_
                            sources_item.save(update_fields=["type"])
                        else:
                            raise Exception("bad type")
                if sources_item.type == 18 or sources_item.type == 20:
                    result, banned = get_all_group_post(session, sources_item.data.split("/")[-1])
                elif sources_item.type == 19 or sources_item.type == 21:
                    result, banned = get_all_profile_post(session, sources_item.data.split("/")[-1])
                else:
                    raise Exception("sources_item.type")
                if banned:
                    sources_item.taken = 0
                    sources_item.disabled = 1
                    sources_item.save(update_fields=['taken', 'last_modified', 'disabled'])
                else:
                    result_count = len(result)
                    django.db.close_old_connections()
                    save_result(result)
                    if len(result) >= 0:
                        sources_item.last_modified = update_time_timezone(timezone.localtime())
                    django.db.close_old_connections()
                    sources_item.taken = 0
                    sources_item.save(update_fields=['taken', 'last_modified'])
        else:
            time.sleep(60)
        if session:
            stop_session(session, attempt=0)

    except Exception as e:
        print("start_task 1" + str(e))
        time.sleep(20)
        try:
            if sources_item:
                stop_source(sources_item, attempt=0)
            if session:
                stop_session(session, attempt=0)
            time.sleep(60)
        except Exception as e:
            print("stop " + str(e))
    return result_count

def check_user_group(sources_item, session_data):
    session = requests.session()
    from login import login as login_
    session = login_(session, session_data.login, session_data.password, session_data)
    if session.get(f"https://ok.ru/{sources_item.data}/members").ok:
        return 18
    if session.get(f"https://ok.ru/{sources_item.data}/friends").ok:
        return 19
    return None


# 18 - group_name
# 19 - user_name
# 20 - group
# 21 - profile

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ok_parser.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    print(1)
    import django

    django.setup()
    import pymysql

    pymysql.install_as_MySQLdb()

    from parse_group import get_all_group_post
    from parse_profile import get_all_profile_post
    from search import get_all_posts
    from accounts import update_time_timezone
    from django.utils import timezone
    import datetime
    from core.models import Posts, Sessions, Keyword, Sources, Owner, AllProxy

    # for o in Owner.objects.all():
    #     screen_prefix = "group"
    #     if len(str(o.id)) < 14:
    #         screen_prefix = "user"
    #     o.screen_prefix = screen_prefix
    #     o.save()

    network_id = 10

    for i in range(2):
        time.sleep(4)
        print("thread ThreadPoolExecutor thread start " + str(i))
        x = multiprocessing.Process(target=new_process_source, args=(i,))
        x.start()

