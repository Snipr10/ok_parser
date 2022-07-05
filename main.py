#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import time

import django.db
import threading
import random
import multiprocessing

import requests


def new_process(i):
    for i in range(9):
        time.sleep(random.randint(1, 5))

        print(f"multiprocessing key {i}")
        x = multiprocessing.Process(target=start_task_while, args=(i,))
        x.start()


def new_process_source(i):
    for i in range(9):
        time.sleep(random.randint(1, 5))
        print(f"multiprocessing source {i}")
        x = multiprocessing.Process(target=start_task_while_source, args=(i,))
        x.start()


def start_task_while_source(i):
    while True:
        try:
            django.db.close_old_connections()
            start_task_source()
        except Exception as e:
            time.sleep(random.randint(5, 10))
            print(e)


def start_task_while(i):
    while True:
        try:
            django.db.close_old_connections()
            start_task()
        except Exception as e:
            time.sleep(random.randint(5, 10))
            print(e)


def start_task_source():
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
        sources_item = SourcesItems.objects.filter(network_id=10, disabled=0, taken=0,
                                                   source_id__in=list(select_sources.values_list('id', flat=True))) \
            .order_by('last_modified').first()

        # time = select_sources.get(id=sources_item.source_id).sources

        if sources_item is not None:
            time_s = select_sources.get(id=sources_item.source_id).sources
            if time_s is None:
                time_s = 0
            if sources_item.last_modified is None or (
                    sources_item.last_modified + datetime.timedelta(minutes=time_s) <
                    update_time_timezone(timezone.localtime())):
                sources_item.taken = 1
                sources_item.save()
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
                    result = get_all_group_post(session, sources_item.data.split("/")[-1])
                elif sources_item.type == 19 or sources_item.type == 21:
                    result = get_all_profile_post(session, sources_item.data.split("/")[-1])
                else:
                    raise Exception("sources_item.type")
                django.db.close_old_connections()
                save_result(result)
        if sources_item:
            sources_item.last_modified = update_time_timezone(timezone.localtime())
            sources_item.taken = 0
            sources_item.save(update_fields=['taken', 'last_modified'])
        if session:
            stop_session(session, attempt=0)

    except Exception as e:
        print("start_task" + str(e))
        time.sleep(20)
        try:
            if sources_item:
                stop_source(sources_item, attempt=0)
            if session:
                stop_session(session, attempt=0)
            time.sleep(60)
        except Exception as e:
            print("stop " + str(e))


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
        print(f"select_sources {select_sources}")

        key_source = KeywordSource.objects.filter(source_id__in=list(select_sources.values_list('id', flat=True)))
        print(f"key_source {key_source}")

        key_word = Keyword.objects.filter(network_id=10, enabled=1, taken=0,
                                          id__in=list(key_source.values_list('keyword_id', flat=True))
                                          ).order_by('last_modified').first()
        print(f"key_word {key_word}")

        if key_word:
            key_word.taken = 1
            key_word.save(update_fields=['taken'])
        else:
            stop_session(session, attempt=0)
            time.sleep(random.randint(100, 150))
        print(f"key_word {key_word}")
        res = get_all_posts(session, key_word.keyword)
        django.db.close_old_connections()
        update_only_time(key_word)
        save_result(res)
        if key_word:
            stop_source(key_word, attempt=0)
        if session:
            stop_session(session, attempt=0)
        time.sleep(60)

    except Exception as e:
        print("start_task" + str(e))
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
    from core.models import Posts, Sessions, Keyword, Sources

    network_id = 10
    # res = get_all_posts(None, "Борис Пиотровский")

    from saver import save_result, get_sphinx_id

    # for p in Posts.objects.all():
    #     if str(p.sphinx_id) == "0":
    #         p.sphinx_id = get_sphinx_id(p.url)
    #         p.save()
    # print("AOK")
    # time.sleep(1000)

    # z = get_all_group_post(None, "fontanka")
    # z = get_all_profile_post(None, "zotov.artem")
    # z = get_all_posts(None, "Рубрика «Оружие Победы» Пулемёт ДП-27")
    for i in range(1):
        time.sleep(4)
        print("thread ThreadPoolExecutor thread start " + str(i))
        x = threading.Thread(target=new_process, args=(i,))
        x.start()

    for i in range(1):
        time.sleep(4)
        print("thread ThreadPoolExecutor thread start " + str(i))
        x = threading.Thread(target=new_process_source, args=(i,))
        x.start()

    i = 1
    while True:
        i += 1
        time.sleep(180)
        try:
            django.db.close_old_connections()
            try:
                Sessions.objects.filter(is_parsing=1,
                                        last_parsing__lte=update_time_timezone(
                                            timezone.now() - datetime.timedelta(minutes=60)),
                                        ).update(is_parsing=0)
            except Exception as e:
                print(e)
            try:
                if i == 100:
                    try:
                        Keyword.objects.filter(network_id=network_id, enabled=1, taken=1).update(taken=0)
                    except Exception as e:
                        print(e)
                    try:
                        Sources.objects.filter(network_id=network_id, taken=1).update(taken=0)
                    except Exception as e:
                        print(e)
                    i = 0
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)
