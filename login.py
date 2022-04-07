def login(session, login_, password_):
    login_headers = {
        'authority': 'ok.ru',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'origin': 'https://ok.ru',
        'upgrade-insecure-requests': '1',
        'dnt': '1',
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://ok.ru/',
        'accept-language': 'ru-RU,ru;q=0.9',
    }
    url = 'https://ok.ru/dk?cmd=AnonymLogin&st.cmd=anonymLogin'

    payload = 'st.redirect=' \
              '&st.asr=' \
              '&st.posted=set' \
              '&st.fJS=on' \
              '&st.st.screenSize=1920%2Bx%2B1080' \
              '&st.st.browserSize=980' \
              '&st.st.flashVer=0.0.0' \
              f'&st.email={login_}' \
              f'&st.password={password_}' \
              '&st.iscode=false'
    res = session.post(url, headers=login_headers, data=payload)
    if "topPanelLeftCorner" not in res.text or "TD_Logout" not in res.text:
        print(res)

        raise Exception("Can not login")

    return session