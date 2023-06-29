#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import time

import django.db
import threading
import random
import multiprocessing

import requests
from bs4 import BeautifulSoup


def new_process(i):
    for i in range(3):
        time.sleep(random.randint(1, 5))
        print(f"multiprocessing key {i}")
        x = threading.Thread(target=start_task_while, args=(i,))
        x.start()


def start_task_while(i):
    while True:
        try:
            django.db.close_old_connections()
            start_task()
        except Exception as e:
            time.sleep(random.randint(5, 10))
            print(e)


def check_user_group(sources_item, session_data):
    session = requests.session()
    from login import login as login_
    session = login_(session, session_data.login, session_data.password, session_data)
    if session.get(f"https://ok.ru/{sources_item.data}/members").ok:
        return 18
    if session.get(f"https://ok.ru/{sources_item.data}/friends").ok:
        return 19
    return None


def start_task():
    from django.db.models import Q

    from core.models import Sources
    from django.utils import timezone
    from accounts import get_new_session
    from accounts import update_time_timezone
    from accounts import stop_session
    from accounts import stop_source
    from utils import update_only_time
    from saver import save_result
    from core.models import KeywordSource, Keyword

    from search import get_all_posts
    key_word = None
    session = None
    try:
        session = get_new_session()
        print(f"session {session}")
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
        # print(f"select_sources {select_sources}")

        key_source = KeywordSource.objects.filter(source_id__in=list(select_sources.values_list('id', flat=True)))
        # print(f"key_source {key_source}")

        key_word = Keyword.objects.filter(network_id=10, enabled=1, taken=0,
                                          id__in=list(key_source.values_list('keyword_id', flat=True)),
                                          last_modified__gte=datetime.date(1999, 1, 1),
                                          ).order_by('last_modified').first()
        # print(f"key_word {key_word}")

        if key_word:
            key_word.taken = 1
            key_word.save(update_fields=['taken'])
            update_only_time(key_word)

        else:
            stop_session(session, attempt=0)
            time.sleep(random.randint(100, 150))
        print(f"key_word {key_word}")
        res = get_all_posts(session, key_word.keyword)
        django.db.close_old_connections()
        print(f"update_only_time {key_word}")
        save_result(res)
        update_only_time(key_word)

        if key_word:
            stop_source(key_word, attempt=0)
        if session:
            stop_session(session, attempt=0)
        time.sleep(60)

    except Exception as e:
        print("start_task2 " + str(e))
        time.sleep(20)
        try:
            if key_word:
                stop_source(key_word, attempt=0)
            if session:
                stop_session(session, attempt=0)
        except Exception as e:
            print("stop " + str(e))


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
        x = multiprocessing.Process(target=new_process, args=(i,))
        x.start()


