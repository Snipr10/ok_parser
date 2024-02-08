#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import multiprocessing
import os
import random
import re
import threading
import time

import django.db
import requests
from bs4 import BeautifulSoup
from django.db.models import Q

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

    import datetime

    from django.utils import timezone

    from accounts import update_time_timezone
    from core.models import (AllProxy, BannedProxy, Keyword, Owner, Posts,
                             Sessions, Sources, SourcesItems)
    from login import get_new_proxy
    from parse_group import get_all_group_post
    from parse_profile import get_all_profile_post
    from search import get_all_posts
    i =0
    print("start")
    for p in Posts.objects.filter(url__contains="https://ok.ruhttps"):
        try:
            i += 1
            print(i)
            p.url = p.url.replace("https://ok.ru" , "")
            p.url = "https://ok.ru/" + p.url
            if "ok.rulive" in p.url:
                p.url = p.url.replace("ok.rulive", "ok.ru/live")

            p.save()
            # if "https://" not in p.url:
            #   p.url = "https://ok.ru" + p.url.replace("%2F", "/")
            #   p.save()
            # elif "ok.rulive" in p.url:
            #     p.url = p.url.replace("ok.rulive", "ok.ru/live")
            #     p.save()
            # else:
            #     p.url = "https://ok.ru" + p.url
            #     p.save()

        except Exception:
            pass