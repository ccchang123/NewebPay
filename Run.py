# python3 -m pip install pycryptodome
import json
import logging
import re
from binascii import a2b_hex
from datetime import datetime

import requests
from Crypto.Cipher import AES
from flask import Flask, abort, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from lib.lib import MpgTrade, Rcon
from Setting import *

app = Flask('', template_folder='', static_folder='')
limiter = Limiter(app, key_func = get_remote_address, storage_uri='memory://')
logging.basicConfig(level=logging.DEBUG, filename='log.log', filemode='a', format='%(asctime)s %(levelname)s: %(message)s')
with open('BanIP.txt', 'r', encoding='utf-8') as file:
    ban_ip_list = file.read().split('\n')
    while True:
        if '' in ban_ip_list:
            ban_ip_list.remove('')
        else:
            break
with open('log.json', 'r', encoding = 'utf-8') as file:
    log = json.load(file)
limiter_times = {}
FORMAT = '%Y-%m-%d, %H:%M:%S'

def time():
    last_time = datetime.strptime('1970-01-01, 00:00:00', FORMAT)
    now_time = datetime.strptime(datetime.now().strftime(FORMAT), FORMAT)
    return ((now_time - last_time).total_seconds())

@app.before_request
def before_request():
    global res
    environ = request.environ
    ip = environ.get('REMOTE_ADDR')
    res = f"{environ.get('REMOTE_ADDR')} - - \"{environ.get('REQUEST_METHOD')} {environ.get('PATH_INFO')} {environ.get('SERVER_PROTOCOL')}\""
    if (BLACKLIST_MODE) and (ip in ban_ip_list) and (environ.get('PATH_INFO') not in ['/css/index.css']):
        logging.warning(f'{ip} try to connect the server, but was refused. (blacklist mode)')
        abort(403)   
    if (WHITELIST_MODE) and (ip not in ban_ip_list) and (environ.get('PATH_INFO') not in ['/css/index.css']):
        logging.warning(f'{ip} try to connect the server, but was refused. (whitelist mode)')
        abort(403)

@app.after_request
def after_request(response):
    ip = request.environ.get('REMOTE_ADDR')
    match str(status_code := response.status_code)[0]:
        case '5':
            logging.error(f'{res} {status_code}')
        case '4':
            if status_code == 429:
                try:
                    limiter_times[ip] = limiter_times[ip] + 1
                except:
                    limiter_times[ip] = 1
                if limiter_times[ip] > 5:
                    logging.warning(f'AutoBan: {ip} too many requests. (429)')
                    ban_ip_list.append(ip)
                    with open('BanIP.txt', 'w', encoding='utf-8') as file:
                        for i in ban_ip_list:
                            file.write(f'{i}\n')
            logging.warning(f'{res} {status_code}')
        case _:
            logging.info(f'{res} {status_code}')
    return response

@app.errorhandler(400)
def Error_400(e):
    return render_template('html/Error.html', code='400', reason='Bad Request', title='錯誤請求'), 400

@app.errorhandler(403)
def Error_403(e):
    return render_template('html/Error.html', code='403', reason='Forbidden', title='拒絕訪問'), 403

@app.errorhandler(404)
def Error_404(e):
    return render_template('html/Error.html', code='404', reason='Page Not Found', title='找不到頁面'), 404

@app.errorhandler(429)
def Error_429(e):
    return render_template('html/Error.html', code='429', reason='Too Many Requests', title='請求次數過多'), 429

@app.errorhandler(500)
def Error_500(e):
    return render_template('html/Error.html', code='500', reason='Internal Server Error', title='伺服器錯誤'), 500

@app.route('/')
@app.route('/index.html')
@limiter.limit("10 per 1 minute")
def main():
    return render_template('index.html')
    
@app.route('/terms')
def terms():
    return render_template('html/Terms.html')

@app.route('/WhySeeThis')
def WhySeeThis():
    return render_template('html/WhySeeThis.html')

@app.route('/end_buy', methods=['POST'])
def end_buy():
    global log
    Aes_code = request.form.get('TradeInfo')
    cryptor = AES.new(KEY.encode('utf-8'), AES.MODE_CBC, IV.encode('utf-8'))
    plain_text = str(cryptor.decrypt(a2b_hex(Aes_code)).decode())
    compiler = re.search('}}', plain_text)
    Result = json.loads(plain_text[0:compiler.end()])
    search_key = Result['Result']['MerchantOrderNo']
    rcon = Rcon()
    print(rcon.run_command(f'bungeedonate {log[search_key]["UUID"]} {Result["Result"]["Amt"] - 30}'))
    del log[search_key]
    with open('log.json', 'w', encoding = 'utf-8') as file:
        json.dump(log, file, indent = 4)
    return ''

@app.route('/check', methods=['POST'])
def check():
    global log
    auth_data = {
        'secret': '6LdSC14hAAAAAJD8CX7IWrnwETwTMK_Eks46JcKf',
        'response': request.form['g-recaptcha-response']
    }
    auth_result = requests.post('https://www.google.com/recaptcha/api/siteverify', data=auth_data)
    try:
        uuid = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{request.form["minecraft_id"]}').json().get('id')
    except:
        uuid = None
    if auth_result.json()['success'] and uuid:
        uuid = f'{uuid[0:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:]}'
        minecraft_id = request.form['minecraft_id']
        email = request.form['email']
        amount = int(request.form['amount']) + 30
        msg = request.form['msg']
        now_time = str(time())[0:-2]
        
        mpg_info = {
            'TimeStamp': now_time,
            'MinecraftID': minecraft_id,
            'UUID': uuid,
            'Amount': amount,
            'Email': email,
            'Messenge': msg
        }

        log[now_time] = mpg_info
        with open('log.json', 'w', encoding = 'utf-8') as file:
            json.dump(log, file, indent = 4)

        logging.info('-'*21 + 'MPG info' + '-'*21)
        logging.info(mpg_info)
        logging.info('-'*50)

        Item = MpgTrade(email, amount, msg, now_time)
        return render_template(
            'html/check.html',
            minecraft_id = minecraft_id,
            email = email,
            amount = amount,
            msg = msg,
            MerchantID = ID,
            Aes_code = Item.Encode_Aes(),
            Sha_code = Item.Encode_Sha(),
            version = '2.0'
        )
    elif not uuid:
        return render_template('index.html', error_code='無效的遊戲ID')
    else:
        return render_template('index.html', error_code='驗證失敗')

if __name__ == "__main__":
    import ssl
    import sys

    from gevent import pywsgi
    app.config['DEBUG'] = True
    WebServer = pywsgi.WSGIServer(('0.0.0.0', SERVER_PORT), app) 
    # , keyfile='key.pem', certfile='cert.pem', ssl_version= ssl.PROTOCOL_SSLv23)
    try:
        logging.info('Server STARTED')
        WebServer.serve_forever()
    except KeyboardInterrupt:
        logging.info('Server CLOSED')
        sys.exit()