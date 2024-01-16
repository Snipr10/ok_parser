import hashlib
import json
import datetime

import django.db
import pika

from core.models import PostContent, Posts, Owner
from ok_parser.settings import FIRST_DATE

batch_size = 200


def save_result(res):
    from ok_parser.settings import rmq_settings

    print("save")
    owners = []
    posts = []
    post_content = []
    owner_id = None
    sphinx_ids = []
    owner_update_username = []
    owner_update_avatar = []

    for r in res:
        group_id = None
        from_id = None
        try:
            url = r["url"]
            if url:
                if "ok.ru" not in url:
                    url = "https://ok.ru" + url
            post_id = post_sphinx_id = get_sphinx_id(url)
        except Exception as e:
            print(f"post_id {e}")

            continue

        try:
            created_date = r['date'] if r['date'] else datetime.datetime.now()
            print("FIRST_DATE")
            if created_date < FIRST_DATE:
                continue
            print("created_date < FIRST_DATE")


            sphinx_id = get_sphinx_id(url)
            sphinx_ids.append(sphinx_id)
            if from_id is None:
                from_id = owner_id
            posts.append(Posts(
                id=post_id,
                owner_id=owner_id,
                from_id=from_id,
                created_date=created_date,
                likes=r['likes'],
                comments=r['comments'],
                reposts=r['share'],
                url=url,
                sphinx_id=sphinx_id,
                content_hash=get_md5_text(r['text'])))
        except Exception as e:
            print(e)

        try:
            group_id = r.get("group_id")
            group_screen = r.get("group_screen")
            if group_screen is None:
                group_screen = group_id
            group_img = r.get("group_img")
            print(r)
            followers = r.get("followers", 0) or 0
            if followers == 0:
                print(r)

            if group_id:
                sphinx_id = get_sphinx_id(group_id)
                owner_id = group_id
                screen_prefix = "group"
                if len(str(group_id)) < 14:
                    screen_prefix = "user"
                owner = Owner(
                        id=group_id,
                        screen_name=group_screen,
                        username=group_id,
                        name=r["name"],
                        avatar=group_img,
                        sphinx_id=sphinx_id,
                        last_modified=datetime.datetime.now(),
                        followers=followers,
                        screen_prefix=screen_prefix
                )
                owners.append(owner)
                print("group_screen: " + str(group_screen) + " " + "group_id: " + str(group_id) + " " +  "followers: " + {followers})
                if r.get("group_screen"):
                    owner_update_username.append(owner)
                if group_img:
                    owner_update_avatar.append(owner)
            screen_name = r.get("from_id")
            from_img = r.get("from_img")
            from_screen = r.get("from_screen")
            if from_screen is None:
                from_screen = screen_name
            if screen_name:
                sphinx_id = get_sphinx_id(screen_name)
                from_id = screen_name
                screen_prefix = "group"
                if len(str(screen_name)) < 14:
                    screen_prefix = "user"
                owner = Owner(
                        id=screen_name,
                        screen_name=from_screen,
                        username=screen_name,
                        name=r['from_name'],
                        avatar=from_img,
                        sphinx_id=sphinx_id,
                        last_modified=datetime.datetime.now(),
                        followers=followers,
                        screen_prefix=screen_prefix
                )
                owners.append(owner)

                if r.get("from_screen"):
                    owner_update_username.append(owner)
                if from_img:
                    owner_update_avatar.append(owner)
            else:
                from_id = owner_id
        except Exception as e:
            print(e)


        try:
            post_content.append(PostContent(id=post_id, content=r['text'], url=r["url"]
                                            ))
        except Exception as e:
            print(e)
    django.db.close_old_connections()

    try:
        Owner.objects.bulk_update(owner_update_username, ['screen_name', 'last_modified', 'followers'], batch_size=batch_size)
    except Exception as e:
        print(f"owner {e}")
    try:
        Owner.objects.bulk_update(owner_update_avatar, ['avatar', 'last_modified', 'followers'], batch_size=batch_size)
    except Exception as e:
        print(f"owner {e}")
    try:
        Owner.objects.bulk_create(owners, batch_size=batch_size, ignore_conflicts=True)
    except Exception as e:
        print(f"owner {e}")

    try:
        Posts.objects.bulk_create(posts, batch_size=batch_size, ignore_conflicts=True)
    except Exception as e:
        print(f"owner {e}")

    try:
        Posts.objects.bulk_update(posts, ['owner_id', 'from_id', 'likes', 'reposts', "comments", "last_modified"], batch_size=batch_size)
    except Exception as e:
        print(f"owner {e}")

    try:
        PostContent.objects.bulk_create(post_content, batch_size=batch_size, ignore_conflicts=True)
    except Exception as e:
        print(f"owner {e}")
    try:
        PostContent.objects.bulk_update(post_content, ["content"], batch_size=batch_size)
    except Exception as e:
        print(f"owner {e}")
    try:
        parameters = pika.URLParameters(rmq_settings)
        connection = pika.BlockingConnection(parameters=parameters)
        channel = connection.channel()
        for sphinx_id in sphinx_ids:
            rmq_json_data = {
                "id": sphinx_id,
                "network_id": 10
            }
            channel.basic_publish(exchange='',
                                  routing_key='post_index',
                                  body=json.dumps(rmq_json_data))
        channel.close()
    except Exception as e:
        print(f"RMQ basic_publish {e}")


def get_sphinx_id(url):
    m = hashlib.md5()
    m.update(('https://m.ok.ru/dk/{}'.format(url)).encode())
    return int(str(int(m.hexdigest()[:16], 16))[:16])


def get_md5_text(text):
    if text is None:
        text = ''
    m = hashlib.md5()
    m.update(text.encode())
    return str(m.hexdigest())
