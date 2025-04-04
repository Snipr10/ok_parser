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
from django.db.models import Q


def new_process(i):
    for i in range(3):
        time.sleep(random.randint(1, 5))
        print(f"multiprocessing key {i}")
        x = threading.Thread(target=start_task_while, args=(i,))
        x.start()


def new_process_source(i):
    for i in range(2):
        time.sleep(random.randint(1, 5))
        print(f"multiprocessing source {i}")
        x = threading.Thread(target=start_task_while_source, args=(i,))
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
        django.db.close_old_connections()
        print(f"session {session}")
        session = get_new_session()
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
                django.db.close_old_connections()
                if banned:
                    sources_item.taken = 0
                    sources_item.disabled = 1
                    sources_item.save(update_fields=['taken', 'last_modified', 'disabled'])
                else:
                    save_result(result)
                    if len(result) > 0:
                        sources_item.last_modified = update_time_timezone(timezone.localtime())
                    sources_item.taken = 0
                    sources_item.save(update_fields=['taken', 'last_modified'])
        else:
            time.sleep(10*60)
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
    from core.models import Posts, Sessions, Keyword, Sources, Owner, AllProxy, SourcesItems, BannedProxy
    from login import get_new_proxy

    network_id = 10
    # from login import login as login_
    # s = Sessions.objects.get(id=368)
    # print(s)
    # session = login_(requests.session(), s.login, s.password, s)
    # print("start")
    #
    # get_all_profile_post("s", "520388205385")
    #
    #
    #
    # print("start")
    # print(AllProxy.objects.all().exclude(id__in=BannedProxy.objects.all().values_list('proxy_id', flat=True)))
    # print("start")
    # print(AllProxy.objects.all())
    # for p in AllProxy.objects.all().exclude(id__in=BannedProxy.objects.all().values_list('proxy_id', flat=True)):
    #     print(p.id)
    #     try:
    #         if requests.get("https://ok.ru/dk?st.cmd=anonymMain", timeout=10,
    #                         proxies={
    #                             'http': f'http://{p.login}:{p.proxy_password}@{p.ip}:{p.port}',
    #                             'https': f'http://{p.login}:{p.proxy_password}@{p.ip}:{p.port}'
    #                         }
    #                         ).ok:
    #             continue
    #     except Exception:
    #         pass
    #     BannedProxy.objects.create(proxy_id=p.id)


    try:
        Sessions.objects.filter(is_parsing=1).update(is_parsing=0)
    except Exception:
            pass
    try:
        SourcesItems.objects.filter(taken=1, network_id=10).update(taken=0)
    except Exception:
            pass
    try:
        Keyword.objects.filter(taken=1, network_id=10).update(taken=0)
    except Exception:
            pass
    try:
        Sessions.objects.filter(is_parsing=1).update(is_parsing=0)
    except Exception:
        pass

    while True:
        try:
            for s in Sessions.objects.filter(is_active__lt=20, proxy_id__isnull=True):
                s.proxy_id = random.choice([969280,
969279,
969278,
969277,
969276,
969275,
                                            969272,
                                            969278,
                                            969279,
                                            969280,
                                            968070,
                                            968071,
                                            ])
                s.is_active = 1
                s.last_parsing = update_time_timezone(timezone.localtime())
                s.save()
        except Exception:
            pass
        try:
            from django.db import connection

            with connection.cursor() as cursor:
                query = """
                UPDATE `prsr_parser_keywords` set `last_modified` = '2000-01-01 00:00:00' WHERE `network_id` = 10 AND `last_modified` = '0000-00-00 00:00:00';
                """
                cursor.execute(query)
        except Exception as e:
            print(e)
        try:
            from django.db import connection

            with connection.cursor() as cursor:
                query = """
                UPDATE `prsr_parser_source_items` set `last_modified` = '2000-01-01 00:00:00' WHERE `network_id` = 10  AND `last_modified` = '0000-00-00 00:00:00';
                """
                cursor.execute(query)
        except Exception as e:
            print(e)
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                query = """
                UPDATE `prsr_parser_keywords` set `last_modified` = '2000-01-01 00:00:00' WHERE `network_id` = 11 AND `last_modified` = '0000-00-00 00:00:00';
                """
                cursor.execute(query)
        except Exception as e:
            print(e)
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                query = """
                UPDATE `prsr_parser_source_items` set `last_modified` = '2000-01-01 00:00:00' WHERE `network_id` = 11  AND `last_modified` = '0000-00-00 00:00:00';
                """
                cursor.execute(query)
        except Exception as e:
            print(e)
        time.sleep(10*60)
    # # i = 14
    # # while True:
    # #     print(i)
    # #     i += 1
    # #     time.sleep(180)
    # #     try:
    # #         django.db.close_old_connections()
    # #         try:
    # #             Sessions.objects.filter(is_parsing=1,
    # #                                     last_parsing__lte=update_time_timezone(
    # #                                         timezone.now() - datetime.timedelta(minutes=60)),
    # #                                     ).update(is_parsing=0)
    # #         except Exception as e:
    # #             try:
    # #                 for s in Sessions.objects.filter(is_parsing=1):
    # #
    # #                     try:
    # #                         s.is_parsing = 0
    # #                         s.save(update_fields=['is_parsing'])
    # #                     except Exception as e:
    # #                         pass
    # #             except Exception:
    # #                 pass
    # #         try:
    # #             for s in Sessions.objects.filter(proxy_id__isnull=True):
    # #                 try:
    # #                     s.proxy_id = get_new_proxy().id
    # #                     s.save()
    # #                 except Exception:
    # #                     pass
    # #         except Exception as e:
    # #             pass
    # #         try:
    # #             # этот костыль, чтобы обновить новые таски  не ловить ошибку с датами
    # #             key_words = Keyword.objects.filter(network_id=10, enabled=1, taken=0,
    # #
    # #                                                last_modified__lt=update_time_timezone(
    # #                                                    datetime.datetime(2000, 1, 1, 0, 0))
    # #                                                ).update(
    # #                 last_modified=update_time_timezone(datetime.datetime(2000, 1, 1, 0, 0)))
    # #
    # #         except Exception as e:
    # #             pass
    # #         try:
    # #             Sessions.objects.filter(is_active__lte=1_000).update(is_active=1)
    # #         except Exception as e:
    # #             try:
    # #                 for s in Sessions.objects.filter(is_active__lte=1_000):
    # #                     try:
    # #                         s.is_active = 1
    # #                         s.save(update_fields=['is_active'])
    # #                     except Exception:
    # #                         pass
    # #             except Exception as e:
    # #                 pass
    # #         try:
    # #             if i == 15:
    # #                 try:
    # #                     SourcesItems.objects.filter(network_id=10, disabled=0, last_modified__isnull=True).update(
    # #                         last_modified=datetime.datetime(2000, 1, 1))
    # #                     SourcesItems.objects.filter(network_id=10, disabled=0,
    # #                                                 last_modified__lte=datetime.datetime(1999, 1, 1)).update(
    # #                         last_modified=datetime.datetime(2000, 1, 1))
    # #                 except Exception as e:
    # #                     print(e)
    # #                 try:
    # #                     Keyword.objects.filter(network_id=network_id, enabled=1, taken=1).update(taken=0)
    # #                 except Exception as e:
    # #                     print(e)
    # #                 try:
    # #                     SourcesItems.objects.filter(network_id=network_id, taken=1).update(taken=0)
    # #                 except Exception as e:
    # #                     print(e)
    # #                 # try:
    #                 #     # Sessions.objects.filter(proxy_id__isnull=False).update(proxy_id=None)
    #                 #     # Sessions.objects.filter(proxy_id__isnull=False).update(proxy_id=None, is_active=0)
    #                 #
    #                 # except Exception as e:
    #                 #     print(e)
    #                 try:
    #                     select_sources = Sources.objects.filter(
    #                         Q(retro_max__isnull=True) | Q(retro_max__gte=timezone.now()), published=1,
    #                         status=1)
    #                     sources_items = SourcesItems.objects.filter(network_id=network_id,
    #                                                                 disabled=0,
    #                                                                 ).exclude(
    #                         source_id__in=list(select_sources.values_list('id', flat=True)))
    #
    #                     sources_items.update(disabled=1)
    #
    #                 except Exception:
    #                     select_sources = Sources.objects.filter(
    #                         Q(retro_max__isnull=True) | Q(retro_max__gte=timezone.now()), published=1,
    #                         status=1)
    #                     select_source_ids = select_sources.values_list('id', flat=True)
    #                     sources_items = SourcesItems.objects.filter(
    #                         network_id=network_id,
    #                         disabled=0,
    #                     )
    #                     for s in sources_items:
    #                         if s.source_id not in select_source_ids:
    #                             s.disabled = 1
    #                             s.save()
    #
    #                 i = 0
    #         except Exception as e:
    #             i = 0
    #             print(e)
    #     except Exception as e:
    #         print(e)
