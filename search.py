import json
import re
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

    while len(result_posts) < 500:
        try:
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
        except Exception:
            pass
    try:
        for post in result_posts:
            try:
                json_res = get_text_html(session, post.get("content"), post)
                if "Вы пока не можете зайти на Одноклассники" in json_res.get("text"):
                    raise Exception("unable to login key search")
                res.append(json_res)
            except ValueError:
                continue
            except Exception as e:
                print(f"get_all_posts {e}")
                try:
                    import requests
                    session = requests.session()
                    session = login(session, session_data.login, session_data.password, session_data)
                except Exception as e:
                    print(f"get_all_posts {e}")
    except Exception as e:
        pass
    return res


def get_followers(resp_bs4):
    followers = 0
    try:
        for s in resp_bs4.find("div", {"class": "menu"}).find_all("div", {"class": "bb"}):
            if "Участники" in s.text:
                followers = int(re.sub(r'[^0-9.]+', r'', s.text))

                break
    except Exception:
        pass
    try:
        if followers == 0:
            try:
                followers = int(re.sub(r'[^0-9.]+', r'', resp_bs4.find("a", {"data-l": "outlandermenu,friendFriend"}).text))
            except Exception:
                followers =  int(re.sub(r'[^0-9.]+', r'', resp_bs4.find("span", {"class": "portlet_h_count"}).text))
    except Exception:
        pass
    print(f"followers: {followers}")
    return followers