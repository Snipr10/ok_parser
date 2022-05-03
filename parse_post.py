import json
import re
import time

import dateparser
from bs4 import BeautifulSoup

types_posts_group = {
    "Movie": {"cmd": "altGroupMovieComments", "st": "sbj"},
    "MediaTopic": {"cmd": "altGroupMediaThemeComments", "st": "themeId"}
}
types_posts_user = {
    "Movie": {"cmd": "movieLayer", "st": "mvId"},
}


def get_text_html(session, posts, r):
    post_bs4 = BeautifulSoup(posts['renderedContent'])
    href = post_bs4.find("a", {"class": "dblock"}).get("href")
    group_id = None
    for q in href.split("&"):
        if "st.groupId=" in q:
            group_id = q.replace("st.groupId=", "")
            break

    if group_id:
        type_post = types_posts_group.get(r['type'])

        url = f"https://m.ok.ru/dk?st.cmd={type_post.get('cmd')}&st.groupId={group_id}&st.{type_post.get('st')}={posts['id']}"
    else:
        type_post = types_posts_user.get(r['type'])
        url = f"https://m.ok.ru/dk?st.cmd={type_post.get('cmd')}&st.{type_post.get('st')}={posts['id']}"
        try:
            group_id = post_bs4.select_one("a", {"class": "dblock"}).attrs.get("href").split("?")[0].split("/")[-1]
        except Exception as e:
            print(e)
    resp = session.get(url, )

    resp_bs4 = BeautifulSoup(resp.text)
    try:
        text_before = resp_bs4.find("span", {"class": "topic-text_before"})
        text_content = resp_bs4.find("span", {"class": "topic-text_content"})
        text = text_before.text + text_content.text
    except Exception as e:
        try:
            text = resp_bs4.find("div", {"class": "outlink_inner_title vdoname"}).text
        except Exception as e:
            try:
                text = json.loads(resp_bs4.select_one('a[data-video*=""]').get("data-video")).get("videoName")
            except Exception as e:
                print(e)
    try:
        date = dateparser.parse(post_bs4.find("div", {"class": "feed_date"}).text)
    except Exception:
        date = None
    try:
        name = resp_bs4.find("a", {"class": "emphased grp"}).text
    except Exception as e:
        try:
            name = post_bs4.select_one("img[alt*='']").attrs.get("alt")
        except Exception:
            print(e)

    likes, comments, share = get_likes_comments_share(resp_bs4)
    group_img = get_img(resp_bs4)
    return {
        "group_id": group_id,
        "group_screen":  None,
        "themeId": posts['id'],
        "text": text,
        "date": date,
        "likes": likes,
        "comments": comments,
        "share": share,
        "type": r['type'],
        "url": url,
        "name": name,
        "group_img": group_img
    }


def get_likes_comments_share(resp_bs4):
    try:
        wigest_list = resp_bs4.find("ul", {"class": "widget-list"}).find_all("li", {"class": "widget-list_i"})
    except Exception:
        wigest_list = None
    try:
        likes = int(wigest_list[-1].find("span", {"class": "widget_count js-count"}).text)
    except Exception:
        try:
            likes = resp_bs4.find("span", {"class": "ecnt"}).text
        except Exception:
            try:
                likes = get_digit(resp_bs4.find_all("a", {"data-type": "LIKE"})[-1].text)
            except Exception:
                likes = 0
    try:
        comments = int(wigest_list[0].find("span", {"class": "widget_count js-count"}).text)
    except Exception:
        try:
            comments = resp_bs4.find("a", {"class": "widget-list_infos_i __COMMENT"}).find("span",
                                                                                           {"class": "ic_tx"}).text
        except Exception:
            try:
                comments = get_digit(resp_bs4.find_all("a", {"href": "#cmntfrm"})[-1].text)
            except Exception:
                comments = 0
    try:
        share = int(wigest_list[1].find("span", {"class": "widget_count js-count"}).text)
    except Exception:
        try:
            share = resp_bs4.find("a", {"class": "widget-list_infos_i __RESHARE"}).find("span", {"class": "ic_tx"}).text

        except Exception:
            try:
                share = get_digit(resp_bs4.find_all("a", {"data-type": "RESHARE"})[-1].text)
            except Exception:
                share = 0

    return likes, comments, share


def get_img(res):
    img = None
    try:
        img = "https:" + res.find("img", {"class": "feed_ava_img"}).get("src")
    except Exception as e:
        try:
            img = "https:" + res.find("a", {"class":"group-avatar-link"}).find("img").get("src")
        except Exception as e:
            img = None
    if img:
        if "i.mycdn.me" in img:
            return img
    return None


def get_digit(str):
    str = re.sub(r'[^0-9]+', r'', str)
    return str or 0
