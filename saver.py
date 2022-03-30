import hashlib

from core.models import SourcesItems, PostContent,Posts,Owner


def save_result(res, s):
    for r in res:
        group_id = r.get("group_id")
        if group_id:
            owner = Owner.objects.filter(screen_name=group_id).first()
            if not owner:
                owner = Owner.objects.create(screen_name=group_id, name=r["name"], sphinx_id=get_sphinx_id(group_id))
            owner_id = owner.id

        else:
            owner_id = None
        try:
            Posts.objects.create(
                id=r['themeId'],
                owner_id=owner_id,
                from_id=owner_id,

                created_date=r['date'],
                likes=r['likes'],
                comments=r['comments'],
                reposts=r['share'],
                url=r["url"],
                content_hash=get_md5_text(r['text']))
        except Exception as e:
            print(e)

        try:
            PostContent.objects.create(id=r['themeId'], content=r['text'], url=r["url"])
        except Exception as e:
            print(e)

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