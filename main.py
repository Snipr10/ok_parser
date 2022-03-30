#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import time

import requests


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
    from saver import save_result

    from login import login
    from search import get_all_posts
    session = requests.session()
    session = login(session)


    _list_ = [
        "телеканал санкт петербург",

        "topspb",
        "комсомольская правда санкт петербург",
        "кп санкт петербург",
        "комсомолка санкт петербург",
        "комсомолка спб",
        "spb kp ru",
        "кп петербург",
        "комсомолка публикует",
        "деловой петербург",
        "dp ru",
        "сообщал дп",
        'материале дп',
        'ранее дп сообщал',


        "писал дп",
        "опрошенные дп",
        "петербургский дневник",
        "spbdnevnik ru",
        "невские новости",
        "nevnov ru",
        "невским новостям",
        "фонтанка ру",
        "fontanka ru",
        "по данным фонтанки",

        "собеседник фонтанки",
        "фонтанка уже рассказывала",
        "материале фонтанки",
        "сообщает фонтанка",
        "фонтанке стало известно",
        "фонтанка писала",
        "издание фонтанка",
        "фонтанка публикует",
        "телеканал 78",
        "78 ru"
    ]
    for s in _list_:
        res = get_all_posts(session, s )
        django.db.close_old_connections()
        save_result(res, s )
        time.sleep(60)