import os

import requests
from bs4 import BeautifulSoup


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
    from login import login

    from core.models import Posts, Sessions, Keyword, Sources, Owner
    # for u in Owner.objects.filter(screen_name__isnull=True, username__isnull=False):
    #     try:
    #         print(u.username)
    #         s = requests.get(f"https://ok.ru/{u.username}")
    #         screen_name=BeautifulSoup(s.text).find("link", {"rel":"alternate"}).get("href").split("/")[-1]
    #         u.screen_name=screen_name
    #         u.save(update_fields=['screen_name'])
    #         print("save")
    #     except Exception as e:
    #         try:
    #             screen_name = BeautifulSoup(s.text).find("div", {"id": "hook_Block_Avatar"}).find("div",
    #                                                                                 {"class": "entity-avatar"}).find(
    #                 "span",
    #                 {
    #                     "class": "__l"}).get(
    #                 "data-id")
    #             u.screen_name = screen_name
    #             u.save(update_fields=['screen_name'])
    #             print("save")
    #         except Exception as e:
    #             print(f"cant get {e}")
    for u in Owner.objects.filter(screen_name__isnull=True):
            print(u.id)
    for u in Owner.objects.filter(screen_name__isnull=True):
        try:
            print(u.id)
            u_id = u.id
            group_id = None
            for p in Posts.objects.filter(from_id=u_id):
                try:
                    url = p.url
                    group_id = url[url.find("&st.groupId=")+12:url.find("&st.themeId=")]
                    if group_id:
                        break
                except Exception as e:
                    print(e)
            if not group_id:
                break
            try:

                s = requests.get(f"https://ok.ru/group/{group_id}")
                print(BeautifulSoup(s.text).find("link", {"rel":"alternate"}))
                username = BeautifulSoup(s.text).find("link", {"rel":"alternate"}).get("href").split("/")[-1]
            except Exception as e:
                username = None
            if username and username == group_id:
                username = None
            u.screen_name = group_id
            u.username = username
            u.save(update_fields=['screen_name', "username"])
            print("save")
        except Exception as e:
            print(f"cant get {e}")
