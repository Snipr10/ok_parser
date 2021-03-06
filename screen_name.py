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
    from saver import get_sphinx_id

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
    from django.db.models import Q
    #
    # for s in Owner.objects.all():
    #     if str(s.screen_name) == str(s.id):
    #         print(s.id)
    #         s.screen_name = None
    #         s.save(update_fields=['screen_name'])
    #
    i = 0

    for p in Posts.objects.all():
        i += 1
        print(i)
        try:
            if p.from_id != p.owner_id:
                print(p.id)
                from_user = Owner.objects.filter(id=p.from_id).first()
                if from_user is  None:
                    continue
                owner_user = Owner.objects.filter(id=p.owner_id).first()
                if owner_user is  None:
                    p.owner_id = p.from_id
                    p.save()
                    continue
                if from_user.name == owner_user.name:
                    p.owner_id = p.from_id
                    p.save()
                    try:
                        owner_user.delete()
                    except Exception as e:
                        print(e)
        except Exception as e:
            print(e)
    # list_user = set()
    # for u in Owner.objects.filter():
    #     if Owner.objects.filter(~Q(id=u.id), screen_name=u.screen_name).exists():
    #         print(u.id)
    #         list_user.add(u.screen_name)
    # for s in list_user:
    #     users = Owner.objects.filter(screen_name=s)
    #     user = None
    #     for u in users:
    #         if get_sphinx_id(u.screen_name) == u.id:
    #             user = u
    #             break
    #     if user:
    #         for u in users:
    #             if u.id != user.id:
    #                 Posts.objects.filter(owner_id=u.id).update(owner_id=user.id)
    #                 Posts.objects.filter(from_id=u.id).update(from_id=user.id)
    #                 u.delete()
    # for u in Owner.objects.filter():
    #     if str(u.id) != str(get_sphinx_id(u.screen_name)):
    #         f_id = u.id
    #         Posts.objects.filter(owner_id=u.id).update(owner_id=get_sphinx_id(u.screen_name))
    #         Posts.objects.filter(from_id=u.id).update(from_id=get_sphinx_id(u.screen_name))
    #         u.id = get_sphinx_id(u.screen_name)
    #         u.sphinx_id = get_sphinx_id(u.screen_name)
    #         u.save()
    #     elif str(u.sphinx_id) != str(get_sphinx_id(u.screen_name)):
    #         u.sphinx_id = get_sphinx_id(u.screen_name)
    #         u.save(update_fields=['sphinx_id'])
    #
    #
    #
    # session = requests.session()
    # session = login(session, "%2B9062570633", "Elena%401996%25", "session_data")
    #
    # for u in Owner.objects.filter(screen_name__isnull=True):
    #     try:
    #         print(u.id)
    #         u_id = u.id
    #         group_id = None
    #         for p in Posts.objects.filter(from_id=u_id):
    #             try:
    #                 url = p.url
    #                 group_id = url[url.find("&st.groupId=")+12:url.find("&st.themeId=")]
    #                 if group_id:
    #                     try:
    #                         int(group_id)
    #                         break
    #                     except Exception as e:
    #                         group_id = None
    #
    #             except Exception as e:
    #                 print(e)
    #         if not group_id:
    #             continue
    #         try:
    #             username = None
    #
    #             s = session.get(f"https://ok.ru/group/{group_id}")
    #             print(BeautifulSoup(s.text).find("link", {"rel":"alternate"}))
    #             username = BeautifulSoup(s.text).find("link", {"rel":"alternate"}).get("href").split("/")[-1]
    #         except Exception as e:
    #             username = None
    #         if username and username == group_id:
    #             username = None
    #         u.screen_name = group_id
    #         u.username = username
    #         u.save(update_fields=['screen_name', "username"])
    #         print("save")
    #     except Exception as e:
    #         print(f"cant get")
    # for u in Owner.objects.filter(screen_name__isnull=True):
    #     u_id = u.id
    #     print(u_id)
    #     if not Posts.objects.filter(from_id=u_id).exists() and not Posts.objects.filter(owner_id=u_id).exists():
    #         u.delete()
    #         print(u_id)
    #
    # https://ok.ru/profile/338318952336/statuses/154563616675984
    # for u in Owner.objects.filter(screen_name__isnull=True):
    #     u_id = u.id
    #
    #     for p in Posts.objects.filter(from_id=u_id):
    #         try:
    #             url = p.url
    #             group_id =url[url.find("profile/")+8:url.find("/statuses")]
    #             if group_id:
    #                 try:
    #                     int(group_id)
    #                     u.screen_name=group_id
    #                     u.save(update_fields=['screen_name'])
    #                     break
    #                 except Exception as e:
    #                     group_id = url[url.find("ok.ru/") + 6:url.find("/statuses")]
    #
    #                     if "/" not in group_id:
    #                         u.username = group_id
    #                         u.save(update_fields=['username'])
    #                         break
    #                     group_id = None
    #         except Exception as e:
    #             print(e)

    # for u in Owner.objects.filter(screen_name__isnull=True):
    #     try:
    #         print(u.id)
    #         u_id = u.id
    #         url = None
    #         for p in Posts.objects.filter(from_id=u_id):
    #             if "movieLayer" in p.url:
    #                 url = p.url
    #                 break
    #         if not url:
    #             continue
    #         s = session.get(url)
    #
    #         url_user = BeautifulSoup(s.text).find("div", {"class": "owner_card"}).find_all("a")[-1].get("href")
    #         group_id = url_user[url_user.find("&st.friendId") + 13:url_user.find("&_prevCmd")]
    #
    #         try:
    #             s = requests.get(f"https://ok.ru/profile/{group_id}")
    #             username = BeautifulSoup(s.text).find("link", {"rel": "canonical"}).get("href").split("/")[-1]
    #         except Exception as e:
    #             username = None
    #
    #         u.screen_name = group_id
    #         u.username = username
    #         u.save(update_fields=['screen_name', "username"])
    #         print("save")
    #     except Exception as e:
    #         print(f"cant get")
    # for u in Owner.objects.filter(screen_name__isnull=True):
    #     try:
    #         ex = Owner.objects.filter(name=u.name, screen_name__isnull=False).first()
    #         if ex:
    #             u.screen_name= ex.screen_name
    #             u.save(update_fields=['screen_name'])
    #     except Exception as e:
    #         print(e)