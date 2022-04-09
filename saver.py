import hashlib

from core.models import PostContent, Posts, Owner

batch_size = 200


def save_result(res):
    print("save")
    owners = []
    posts = []
    post_content = []
    owner_id = None
    for r in res:
        group_id = None
        try:
            group_id = r.get("group_id")
            if group_id:
                owner_id = get_sphinx_id(group_id)
                owners.append(Owner(id=owner_id, screen_name=group_id, name=r["name"], sphinx_id=get_sphinx_id(group_id)))
            from_id = r.get("from_id")
            if from_id:
                from_id = get_sphinx_id(from_id)
                owners.append(
                    Owner(id=from_id, screen_name=from_id, name=r['from_name'], sphinx_id=get_sphinx_id(from_id)))
            else:
                from_id = owner_id
        except Exception as e:
            print(e)
        try:
            posts.append(Posts(
                id=r['themeId'],
                owner_id=owner_id,
                from_id=from_id,
                created_date=r['date'],
                likes=r['likes'],
                comments=r['comments'],
                reposts=r['share'],
                url=r["url"],
                content_hash=get_md5_text(r['text'])))
        except Exception as e:
            print(e)

        try:
            post_content.append(PostContent(id=r['themeId'], content=r['text'], url=r["url"]))
        except Exception as e:
            print(e)

    try:
        Owner.objects.bulk_create(owners, batch_size=batch_size, ignore_conflicts=True)
    except Exception as e:
        print(f"owner {e}")

    try:
        Posts.objects.bulk_create(posts, batch_size=batch_size, ignore_conflicts=True)
    except Exception as e:
        print(f"owner {e}")

    try:
        Posts.objects.bulk_update(posts, ['owner_id', 'from_id'], batch_size=batch_size)
    except Exception as e:
        print(f"owner {e}")

    try:
        PostContent.objects.bulk_create(post_content, batch_size=batch_size, ignore_conflicts=True)
    except Exception as e:
        print(f"owner {e}")


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