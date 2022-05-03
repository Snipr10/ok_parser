import json
import time

from parse_post import get_text_html


def search_posts(session, query, count, firstIndex, totalCount=None):
    url = "https://ok.ru/web-api/v2/search/portal"
    payload = json.dumps({
        "id": 1,
        "parameters": {
            "query": query,
            "filters": {
                "st.cmd": "searchResult",
                "st.mode": "Content",
                "st.query": query,
                "st.grmode": "Groups"
            },
            "chunk": {
                "count": count,
                "firstIndex": firstIndex,
                "offset": 0
            },
            "meta": {
                "prefetch": False,
                "voice": False
            }
        }
    })

    headers = {
        'Content-Type': 'application/json',
    }

    result = session.post(url, headers=headers, data=payload)

    res = result.json()
    if res['result']['content']['totalCount'] == 0:
        return [], totalCount, False
    return res['result']['content']['results'], res['result']['content']['totalCount'], True


def get_all_posts(session_data, query):
    from login import login
    import requests
    print("get_all_posts")
    session = requests.session()
    session = login(session, session_data.login, session_data.password, session_data)

    count = 50
    firstIndex = 0
    totalCount = None
    result_posts = []
    res = []

    while True:
        print("while")
        posts, totalCount, is_next = search_posts(session, query, count, firstIndex, totalCount=totalCount)
        if not is_next:
            break
        result_posts.extend(posts)
        if totalCount <= count:
            break
        firstIndex += count
        if totalCount < firstIndex + count:
            count = totalCount - firstIndex
        time.sleep(1.5)
    for post in result_posts:
        try:
            res.append(get_text_html(session, post.get("content"), post))
        except Exception as e:
            import requests
            session = requests.session()
            session = login(session, session_data.login, session_data.password, session_data)

    return res