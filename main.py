#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import time

import django.db
import threading
import random
import multiprocessing

def new_process(i):
    for i in range(9):
        time.sleep(random.randint(1, 5))

        print(f"multiprocessing {i}")
        x = multiprocessing.Process(target=start_task_while, args=(i,))
        x.start()

def start_task_while(i):
    while True:
        try:
            django.db.close_old_connections()
            start_task()
        except Exception as e:
            time.sleep(random.randint(5, 10))
            print(e)


def start_task():
    from django.db.models import Q

    from core.models import Sources, SourcesItems
    from django.utils import timezone
    from accounts import get_new_session
    from accounts import update_time_timezone
    from accounts import stop_session
    from accounts import stop_source
    from utils import update_only_time
    from saver import save_result
    from core.models import KeywordSource, Keyword

    from login import login
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
                                           ).order_by('last_modified').last()
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

    for i in range(1):
        time.sleep(4)
        print("thread ThreadPoolExecutor thread start " + str(i))
        x = threading.Thread(target=new_process, args=(i,))
        x.start()










    #
    #
    #
    # from saver import save_result
    #
    # from login import login
    # from search import get_all_posts
    #
    # session = requests.session()

    # session = login(session, login_, password_)
    #
    # _list_ = [
    #     "телеканал санкт петербург",
    #
    #     "topspb",
    #     "комсомольская правда санкт петербург",
    #     "кп санкт петербург",
    #     "комсомолка санкт петербург",
    #     "комсомолка спб",
    #     "spb kp ru",
    #     "кп петербург",
    #     "комсомолка публикует",
    #     "деловой петербург",
    #     "dp ru",
    #     "сообщал дп",
    #     'материале дп',
    #     'ранее дп сообщал',
    #
    #     "писал дп",
    #     "опрошенные дп",
    #     "петербургский дневник",
    #     "spbdnevnik ru",
    #     "невские новости",
    #     "nevnov ru",
    #     "невским новостям",
    #     "фонтанка ру",
    #     "fontanka ru",
    #     "по данным фонтанки",
    #
    #     "собеседник фонтанки",
    #     "фонтанка уже рассказывала",
    #     "материале фонтанки",
    #     "сообщает фонтанка",
    #     "фонтанке стало известно",
    #     "фонтанка писала",
    #     "издание фонтанка",
    #     "фонтанка публикует",
    #     "телеканал 78",
    #     "78 ru"
    # ]
    # django.db.close_old_connections()
    #
    # for s in _list_:
    #     print(s)
    #     res = get_all_posts(session, s)
    #     django.db.close_old_connections()
    #     save_result(res, s)
    #     time.sleep(60)
