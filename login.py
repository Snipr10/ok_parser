import random

import requests
from twocaptcha import TwoCaptcha

from core.models import AllProxy, BannedProxy
from ok_parser.settings import two_captcha

solver = TwoCaptcha(two_captcha)


def get_new_proxy():
    for p in AllProxy.objects.filter(port__in=[9673, 9651, 9875, 8000]).order_by('?'):
        proxies = {
            'http': f'http://{p.login}:{p.proxy_password}@{p.ip}:{p.port}',
            'https': f'http://{p.login}:{p.proxy_password}@{p.ip}:{p.port}'
        }
        try:
            if requests.get("https://ok.ru/dk?st.cmd=anonymMain", timeout=10, proxies=proxies).ok:
                return p
        except Exception:
            pass
    return None
    # return AllProxy.objects.exclude(
    #     id__in=BannedProxy.objects.all().values_list('proxy_id', flat=True)
    # ).order_by('?').first()



def login(session, login_, password_, session_data=None, attempt=0):
    if session_data is None:
        raise Exception(f"session_data Null")

    if attempt > 5:
        session_data.is_parsing = 0
        session_data.is_active += 1
        session_data.proxy_id = None
        session_data.save(update_fields=['proxy_id', 'is_active', 'proxy_id'])
        raise Exception(f"attempt login attempt {session_data.id}")

    print(f"start login {session_data} {session_data.proxy_id}")
    try:
        session_proxy = AllProxy.objects.get(id=session_data.proxy_id)
        proxy_2_cap = None

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
        print(proxies, session_data)
        proxy_2_cap = {'type': 'HTTP',
                       'uri': f'{session_proxy.login}:{session_proxy.proxy_password}@{session_proxy.ip}:{session_proxy.port}'}
    except Exception as e:
        try:
            BannedProxy.objects.create(proxy_id=session_data.proxy_id)
        except Exception:
            pass
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
        print(res.status_code, session_data)
    except Exception as e:
        try:
            BannedProxy.objects.create(proxy_id=session_data.proxy_id)
        except Exception:
            pass
        print(f"Exp 1 {e}")
        if "ERROR_ZERO_CAPTCHA_FILESIZE" in str(e) or "HTTPSConnectionPool" in str(e):
            if session_data.is_active > 20:
                try:
                    session_data.proxy_id = get_new_proxy().id
                except Exception:
                    session_data.proxy_id = None
                session_data.is_active += 1
            session_data.save(update_fields=['proxy_id', 'is_active'])
        return login(requests.session(), login_, password_, session_data, attempt)

    if "Доступ к профилю ограничен" in res.text \
            or "Неправильно указан логин" in res.text\
            or "Ваш профиль заблокирован за нарушение правил пользования сайтом" in res.text:
        session_data.is_active += 15_000
        session_data.is_parsing = 0

        session_data.save(update_fields=['is_active', 'is_parsing'])
        raise Exception(f"Can not login block {session_data.id}")
    # elif "Проверьте ваше соединение с интернетом и повторите попытку." in res.text:
    #     print("плохая прокси")
    #     try:
    #         session_data.proxy_id = AllProxy.objects.order_by('?').first().id
    #     except Exception:
    #         session_data.proxy_id = None
    #     session_data.save(update_fields=['proxy_id'])
    #     return login(session, login_, password_, session_data, attempt)

    elif "topPanelLeftCorner" not in res.text or "TD_Logout" not in res.text:
        print(f"topPanelLeftCorner 1")

        res = session.get("https://ok.ru/")
        if "topPanelLeftCorner" not in res.text or "TD_Logout" not in res.text:

            if "st.cmd=anonymUnblockConfirmPhone" in res.text:
                print("anonymUnblockConfirmPhone", session_data)
                session_data.is_active += 10_000
                session_data.is_parsing = 0
                session_data.save(update_fields=['is_active', 'is_parsing'])
                raise Exception(f"Blocked {session_data}")

            attempt += 1
            if attempt > 5:
                session_data.is_active += 1
                session_data.is_parsing = 0
                session_data.proxy_id = None

                session_data.save(update_fields=['is_active', 'is_parsing', 'proxy_id'])
                raise Exception(f"Can not login attemps {session_data.id}")
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
                print(f"captcha {e} {session_data}")
                if "ERROR_ZERO_CAPTCHA_FILESIZE" in str(e) or "HTTPSConnectionPool" in str(e):
                    if session_data.is_active > 20:
                        try:
                            BannedProxy.objects.create(proxy_id=session_data.proxy_id)
                        except Exception:
                            pass
                        try:
                            session_data.proxy_id = get_new_proxy().id
                        except Exception:
                            session_data.proxy_id = None
                    session_data.is_active = 0

                    session_data.save(update_fields=['proxy_id', 'is_active'])
                pass
            url = "https://ok.ru/dk?cmd=AnonymVerifyCaptchaEnter&st.cmd=anonymVerifyCaptchaEnter"

            payload = {'st.ccode': code,
                       'st.r.validateCaptcha': 'Готово!'}
            session.post(url, data=payload)
            attempt += 1
            return login(requests.session(), login_, password_, session_data, attempt)
    print(f"login success {session_data}")
    return session
