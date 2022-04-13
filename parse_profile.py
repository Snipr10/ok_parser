import re
import time
import dateparser

from bs4 import BeautifulSoup


def get_all_profile_post(session_data, query):
    from login import login
    import requests
    print("get_all_group_post")
    session = requests.session()
    session = login(session, session_data.login, session_data.password)

    res = []
    try:
        int(query)
        pre_url = f"https://ok.ru/profile/{query}"
    except Exception:
        pre_url = f"https://ok.ru/{query}"

    result = []

    first_resp = session.get(pre_url)
    resp_bs4_first = BeautifulSoup(first_resp.text)
    res.extend(resp_bs4_first.find_all("div", {"class": "feed-w"}))
    markerB = get_markerB(resp_bs4_first)
    # tkn = re.search(r"OK.tkn.set\S\S\w+", first_resp.text).group(0)
    # tkn = tkn.replace('OK.tkn.set(\'',"")

    tkn = re.search(r"OK.tkn.set\S+", first_resp.text).group(0)

    tkn = tkn.replace('OK.tkn.set(\'', "")
    tkn = tkn.split("'")[0]


    group_id = re.search(r"st.groupId=\S\S\w+", first_resp.text).group(0)
    group_id = group_id.replace("st.groupId=", "")

    name = None
    try:
        try:
            name = resp_bs4_first.find("a", {"class":"profile-user-info_name"}).text
        except Exception:
            for r in res:
                for i in r.select("feed_top"):
                    if i.attrs.get("alt"):
                        name = i.attrs.get("alt")
                        break
                if name:
                    break
    except Exception:
        pass

    for r in res:
        res_dict = get_result(r)
        if res_dict:
            res_dict["group_id"] = query
            res_dict["name"] = name
            result.append(res_dict)

    time.sleep(10)
    while True:
        if not markerB:
            break
        url = f"{pre_url}?cmd=FriendFeedsMRB&st.cmd=friendMain&st.friendId={query}"
        headers = {
            'authority': 'ok.ru',
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'dnt': '1',
            'ok-screen': 'friendMain',
            'origin': 'https://ok.ru',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'strd': 'false',
            'tkn': tkn,
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
        }
        payload = f'st.data-bytes-marker={markerB}'
        resp = session.post(url, headers=headers, data=payload)
        resp_bs4 = BeautifulSoup(resp.text)
        markerB = get_markerB(resp_bs4)
        time.sleep(2)
        for r in resp_bs4.find_all("div", {"class": "feed-w"}):
            res_dict = get_result(r)
            if res_dict:
                res_dict["group_id"] = query
                res_dict["name"] = name
                result.append(res_dict)
    return result


def get_markerB(resp_bs4):
    markerB = None
    for i in resp_bs4.find_all("div", {"class":"invisible"}):
        try:
            markerB = i.attrs['st.data-bytes-marker']
            break
        except Exception:
            pass
    return markerB


def get_result(res):
    from parse_post import get_likes_comments_share

    try:
        date = dateparser.parse(res.find("div", {"class": "feed_date"}).text)
        likes, comments, share = get_likes_comments_share(res)
        try:
            from_name = res.select_one("img[alt*='']").attrs.get("alt")
        except Exception:
            from_name = None
        try:
            from_id = res.find("a", {"class":"dblock"}).get("href").split("/")[-1].split("?")[0]
        except Exception:
            from_id = None
        theme_id = re.search(r'gId":"\d+"', str(res)).group(0).replace('gId":"',"").replace('"',"")
        try:
            text = res.find("div", {"class": "media-text_cnt"}).text
        except Exception:
            text = None
        try:
            url = res.find("a", {"class": "media-text_a"}).get("href").split("?")[0]
        except Exception:
            try:
                url = res.find("a", {"class": ""}).get("href").split("?")[0]
            except Exception:
                try:
                    url = re.search(r'st.layer.curl=\S+', str(res)).group(0).replace('st.layer.curl=',"").split("&")[0]
                except Exception:
                    url = None
        return {
            "themeId": theme_id,
            "text": text,
            "date": date,
            "likes": likes,
            "comments": comments,
            "share": share,
            "url": url,
            "from_name": from_name,
            "from_id": from_id
        }
    except Exception as e:
        print(e)
        return None
