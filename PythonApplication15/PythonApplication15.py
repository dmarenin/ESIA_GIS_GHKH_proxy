import requests
import json
import time
from flask import Flask, request
import datetime


app = Flask(__name__)


@app.errorhandler(Exception)
def handle_exception(e):
    return str(e), 500

@app.route('/get_data', methods=['POST'])
def get_data():
    args = request.args.to_dict()

    message = request.data.decode('utf-8')

    message = json.loads(message)

    phone, password, ogrn = message['phone'], message['password'], message['ogrn']

    browser = get_browser()
    sessionId = get_session_id(browser, phone, password, ogrn)

    res = get_data_objs(sessionId, message)

    browser.close()

    browser.quit()

    browser = None

    return json.dumps(res), 200, {'ContentType':'application/json'}

@app.route('/update_data', methods=['POST'])
def update_data():
    args = request.args.to_dict()

    message = request.data.decode('utf-8')

    message = json.loads(message)

    phone, password, org = message['phone'], message['password'], message['ogrn']

    browser = get_browser()
    sessionId = get_session_id(browser, phone, password, org)

    res = []

    for d in message['items']:
        lastUpdate = int(datetime.datetime.now().timestamp()*10)
        #1604179900335

        #r = update_data(sessionId, d, lastUpdate)

        #res.append(r)

    browser.close()

    browser.quit()

    browser = None

    return json.dumps(res), 200, {'ContentType':'application/json'}

def get_data_objs(sessionId, message):
    headers = {'Content-Type':'application/json;charset=UTF-8'}
    cookies = {'sessionId':sessionId}
    payload = {'addressSearchCriteria': {'regionRef': {'code': '54049357-326d-4b8f-b224-3c6dc25d6dd3'}}, 'types': []} 

    url = 'https://my.dom.gosuslugi.ru/agreements/api/rest/services/agreements/social/rent/search;page=1;itemsPerPage='+str(message['itemsPerPage'])

    if not message.get('statuses') is None:
        payload['statuses'] = message.get('statuses')

    if not message.get('period') is None:
        payload['period'] = message.get('period')

    if message.get('numbers') is None:
        payload_txt = json.dumps(payload)

        r = requests.post(url, headers=headers, cookies=cookies, data=payload_txt)

        print("get_data ->  "+str(r.content))

        return json.loads(r.content)

    else:
        res = {'items':[]}
        for d in message['numbers']:
            payload['number'] = d

            payload_txt = json.dumps(payload)

            r = requests.post(url, headers=headers, cookies=cookies, data=payload_txt)

            print("get_data ->  "+str(r.content))

            r = json.loads(r.content)

            res['items'] = res['items'] + r['items']

        return res

def update_data_objs(sessionId, entityGuid, lastUpdate):
    headers = {'Content-Type':'application/json;charset=UTF-8'}
    cookies = {'sessionId':sessionId}
    payload = {'entityGuid':entityGuid, 'lastUpdate':lastUpdate}

    payload = json.dumps(payload)

    url = 'https://my.dom.gosuslugi.ru/agreements/api/rest/services/agreements/social/rent/approval'

    r = requests.put(url, headers=headers, cookies=cookies, data=payload)

    print("update_dat ->  "+str(r.content))

    return json.loads(r.content)

def get_session_id(browser, phone, password, ogrn):
    delay_load_el_by_class_name(browser, "portal-header__signin-action")

    browser.find_element_by_class_name("portal-header__signin-action").click()

    delay_load_el_by_id(browser, "mobileOrEmail")

    el = browser.find_element_by_id("mobileOrEmail")
    el.clear()
    el.send_keys(phone)

    el = browser.find_element_by_id("password")
    el.clear()
    el.send_keys(password)

    delay_load_el_by_id(browser, "loginByPwdButton")

    el = browser.find_element_by_id("loginByPwdButton").click()

    time.sleep(3)

    org = None

    for i in range(0, 50):
        try:
            el_text = browser.find_element_by_id('org'+str(i)).text
            if ogrn in el_text:
                org = str(i)
                break
        except:
            pass

    if ogrn is None:
        raise Exception('ogrn not found')

    shell = """return (function () {return orgPage.selectOrg("""+org+""");}) ()"""
    browser.execute_script(shell)

    delay_load_el_by_id(browser, "saveCookie")

    browser.find_element_by_id("saveCookie").click()

    shell = """return (function () {return continueToPK()}) ()"""
    browser.execute_script(shell)

    time.sleep(3)

    browser.get('https://my.dom.gosuslugi.ru/organization-cabinet/#!/agreements/socialrent')

    session_id = None

    cookies = browser.get_cookies()
    for c in cookies:
        if c['name']=='sessionId':
            session_id = c['value']

    return session_id

def get_browser():
    from selenium import webdriver

    url, path_driver = f'https://dom.gosuslugi.ru/#!/main', "C:/Users/dmarenin/source/repos/PythonApplication15/PythonApplication15/operadriver.exe"

    options = webdriver.ChromeOptions()

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-extensions")

    browser = webdriver.Chrome(path_driver, chrome_options=options)
    browser.delete_all_cookies()
    browser.get(url)

    #browser.minimize_window()

    time.sleep(1)

    return browser

def delay_load_el_by_class_name(browser, class_name):
    el_exist = False
    while not el_exist:
        try:
            browser.find_element_by_class_name(class_name)
            el_exist = True
        except:
            time.sleep(0.5)

    pass

def delay_load_el_by_id(browser, id):
    el_exist = False
    while not el_exist:
        try:
            browser.find_element_by_id(id)
            el_exist = True
        except:
            time.sleep(0.5)

    pass

if __name__ == '__main__':
    HOST = '0.0.0.0'
    PORT = 8095

    app.run(HOST, PORT, threaded=True)

