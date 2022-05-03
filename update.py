#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import time

import django.db
import threading
import random
import multiprocessing



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
    from core.models import Owner, Posts

    from parse_group import get_all_group_post
    from parse_profile import get_all_profile_post
    from search import get_all_posts

    owners = list(Owner.objects.all())
    i = 0
    owners_delete = []
    for o in owners:
        i += 1
        print(i)
        if o.sphinx_id != o.id:
            for p in Posts.objects.filter(owner_id=o.id):
                p.owner_id=o.sphinx_id
                p.save()
            for p in Posts.objects.filter(from_id=o.id):
                p.from_id= o.sphinx_id
                p.save()
        try:
            Owner.objects.create(
                id=o.sphinx_id,
                screen_name=o.screen_name,
                username=o.username,
                name=o.name,
                avatar=o.avatar,
                sphinx_id=o.sphinx_id
            )
        except Exception as e:
            print(e)
        try:
            if o.sphinx_id != o.id:
                o.delete()
                print("DELETE")
        except Exception as e:
            print(e)
    # while len(owners) > 0:
    #     i += 1
    #     print(i)
    #     owner_id = []
    #     owner_new = []
    #
    #     owner = owners.pop()
    #     owner_id.append(owner)
    #     for o in owners:
    #         if o.screen_name == owner.screen_name:
    #             owner_id.append(o)
    #         else:
    #             for z in owners:
    #                 if z.screen_name == owner.screen_name and z.id !=owner.id :
    #                     owner_new.append(o)
    #                     break
    #     owners = owner_new
    #
    #     id_ = owner.sphinx_id
    #     real_owner = None
    #     for ow in owner_id:
    #         if ow.id == id_:
    #             real_owner = ow
    #             break
    #     if not real_owner:
    #         try:
    #             real_owner = Owner(
    #                         id=id_,
    #                         screen_name=owner.screen_name,
    #                         username=owner.username,
    #                         name=owner.name,
    #                         avatar=owner.avatar,
    #                         sphinx_id=id_
    #                 )
    #         except Exception:
    #             continue
    #
    #     for o_id in owner_id:
    #         for p in Posts.objects.filter(owner_id=o_id.id):
    #             p.owner_id=real_owner.id
    #             p.save()
    #         for p in Posts.objects.filter(from_id=o_id.id):
    #             p.from_id=real_owner.id
    #             p.save()
    #
    #     for o_id in owner_id:
    #         if o_id.id != real_owner.id:
    #             o_id.delete()
        # is_bad_screen_name = False
        # try:
        #     int(owner.screen_name)
        # except Exception as e:
        #     is_bad_screen_name = True
        # if is_bad_screen_name:

