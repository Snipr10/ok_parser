import random

from twocaptcha import TwoCaptcha

from ok_parser.settings import two_captcha

solver = TwoCaptcha(two_captcha)


def login(session, login_, password_, session_data=None, attempt=0):
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
        if "st.cmd=anonymUnblockConfirmPhone" in res.text:
            print("anonymUnblockConfirmPhone")
            session_data.is_active = 11
            session_data.save(update_fields=['is_active'])
            raise Exception("Blocked")

        attempt += 1
        if attempt > 5:
            session_data.is_active = 11
            session_data.save(update_fields=['is_active'])
            raise Exception("Can not login")
        attempt += 1
        res_cap = session.get("https://ok.ru/captcha?st.cmd=captcha")
        text = res_cap.content
        file_name = f"{login_}{random.randint(0,100)}.jpg"
        print(file_name)
        fp = open(file_name, 'wb')
        fp.write(text)
        fp.close()
        code = ""
        try:
            code = solver.normal(file_name, lang="ru")['code']
        except Exception as e:
            print(f"captcha {e}")
            pass
        url = "https://ok.ru/dk?cmd=AnonymVerifyCaptchaEnter&st.cmd=anonymVerifyCaptchaEnter"

        payload = {'st.ccode': code,
                   'st.r.validateCaptcha': 'Готово!'}
        session.post(url, data=payload)
        return login(session, login_, password_, session_data, attempt)
    return session
