import random

from twocaptcha import TwoCaptcha

from core.models import AllProxy
from ok_parser.settings import two_captcha

solver = TwoCaptcha(two_captcha)


def login(session, login_, password_, session_data=None, attempt=0):
    print("start login")
    try:
        session_proxy = AllProxy.objects.get(id=session_data.proxy_id)
        # hosts = [
        #     "45.140.75.180",
        #     "45.140.73.86",
        #     "212.162.133.127",
        #     "212.162.134.48",
        #     "212.162.135.52",
        #
        # ]
        # host = random.choice(hosts)
        proxies = {
            'http': f'http://{session_proxy.login}:{session_proxy.proxy_password}@{session_proxy.ip}:{session_proxy.port}',
            'https': f'http://{session_proxy.login}:{session_proxy.proxy_password}@{session_proxy.ip}:{session_proxy.port}'
        }
        session.proxies.update(proxies)
        print(proxies)
        proxy_2_cap = {'type': 'HTTP',
                       'uri': f'{session_proxy.login}:{session_proxy.proxy_password}@{session_proxy.ip}:{session_proxy.port}'}
    except Exception as e:
        proxy_2_cap = None
        print(f"Proxy error : {e}")
    ""
    login_headers = {
        'authority': 'ok.ru',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'ru-RU,ru;q=0.9',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'dnt': '1',
        'origin': 'https://ok.ru',
        'referer': 'https://ok.ru/dk?st.cmd=anonymMain&st.layer.cmd=PopLayerClose',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
    }
    url = 'https://ok.ru/dk?cmd=AnonymLogin&st.cmd=anonymLogin'

    payload = 'st.redirect=' \
              '&st.asr=' \
              '&st.posted=set' \
              '&st.fJS=on' \
              '&st.st.screenSize=1920%2Bx%2B1080' \
              '&st.st.browserSize=948' \
              '&st.st.flashVer=0.0.0' \
              f'&st.email={login_}' \
              f'&st.password={password_}' \
              '&st.iscode=false'
    try:
        res = session.post(url, headers=login_headers, data=payload)
    except Exception as e:
        print(f"Exp 1 {e}")
        if "ERROR_ZERO_CAPTCHA_FILESIZE" in str(e) or "HTTPSConnectionPool" in str(e):
            try:
                session_data.proxy_id = AllProxy.objects.order_by('?').first().id
            except Exception:
                session_data.proxy_id = None
            session_data.save(update_fields=['proxy_id'])
        return login(session, login_, password_, session_data, attempt)
    print(res.text)

    if "Доступ к профилю ограничен" in res.text:
        session_data.is_active = 15
        session_data.save(update_fields=['is_active'])
        raise Exception(f"Can not login block {session.id}")
    elif "topPanelLeftCorner" not in res.text or "TD_Logout" not in res.text:
        print(f"topPanelLeftCorner 1")

        res = session.get("https://ok.ru/")
        if "topPanelLeftCorner" not in res.text or "TD_Logout" not in res.text:

            if "st.cmd=anonymUnblockConfirmPhone" in res.text:
                print("anonymUnblockConfirmPhone")
                session_data.is_active = 11
                session_data.save(update_fields=['is_active'])
                raise Exception("Blocked")

            attempt += 1
            if attempt > 5:
                session_data.is_active += 1
                session_data.save(update_fields=['is_active'])
                raise Exception(f"Can not login attemps {session.id}")
            attempt += 1
            res_cap = session.get("https://ok.ru/captcha?st.cmd=captcha")
            text = res_cap.content
            file_name = f"{login_}{random.randint(0, 100)}{random.randint(0, 100)}{random.randint(0, 100)}{random.randint(0, 100)}.jpg"
            fp = open(file_name, 'wb')
            fp.write(text)
            fp.close()
            code = ""
            try:
                print(f"proxy_2_cap 1")

                if proxy_2_cap:
                    code = solver.normal(file_name, lang="ru", proxy=proxy_2_cap)['code']
                else:
                    code = solver.normal(file_name, lang="ru")['code']

            except Exception as e:
                print(f"captcha {e}")
                if "ERROR_ZERO_CAPTCHA_FILESIZE" in str(e) or "HTTPSConnectionPool" in str(e):
                    try:
                        session_data.proxy_id = AllProxy.objects.order_by('?').first().id
                    except Exception:
                        session_data.proxy_id = None
                    session_data.save(update_fields=['proxy_id'])
                pass
            url = "https://ok.ru/dk?cmd=AnonymVerifyCaptchaEnter&st.cmd=anonymVerifyCaptchaEnter"

            payload = {'st.ccode': code,
                       'st.r.validateCaptcha': 'Готово!'}
            session.post(url, data=payload)
            return login(session, login_, password_, session_data, attempt)
    return session
