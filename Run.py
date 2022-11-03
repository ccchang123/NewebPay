# python3 -m pip install pycryptodome
import json
import logging
import re
from binascii import a2b_hex
from datetime import datetime

import requests
from Crypto.Cipher import AES
from flask import Flask, render_template, request

from lib.lib import MpgTrade, Rcon
from Setting import ID, IV, KEY

app = Flask('', template_folder='', static_folder='')
logging.basicConfig(level=logging.DEBUG, filename='log.log', filemode='a', format='%(asctime)s %(levelname)s: %(message)s')
log = {}
FORMAT = '%Y-%m-%d, %H:%M:%S'

def time():
    last_time = datetime.strptime('1970-01-01, 00:00:00', FORMAT)
    now_time = datetime.strptime(datetime.now().strftime(FORMAT), FORMAT)
    return ((now_time - last_time).total_seconds())

@app.before_request
def before_request():
    global res
    environ = request.environ
    res = f"{environ.get('REMOTE_ADDR')} - - \"{environ.get('REQUEST_METHOD')} {environ.get('PATH_INFO')} {environ.get('SERVER_PROTOCOL')}\""

@app.after_request
def after_request(response):
    match str(status_code := response.status_code)[0]:
        case '5':
            logging.error(f'{res} {status_code}')
        case '4':
            logging.warning(f'{res} {status_code}')
        case _:
            logging.info(f'{res} {status_code}')
    return response

@app.route('/')
@app.route('/index.html')
def main():
    return render_template('index.html')

@app.route('/end_buy', methods=['POST', 'GET'])
def end_buy():
    print(request.form.get('TradeInfo'))
    Aes_code = request.form.get('TradeInfo')
    cryptor = AES.new(KEY.encode('utf-8'), AES.MODE_CBC, IV.encode('utf-8'))
    plain_text = str(cryptor.decrypt(a2b_hex(Aes_code)).decode())
    compiler = re.search('}}', plain_text)
    Result = json.loads(plain_text[0:compiler.end()])
    print(Result['Result']['Amt'])
    return render_template('html/end_buy.html')

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

        logging.info('-'*21 + 'MPG info' + '-'*21)
        logging.info(mpg_info)
        logging.info('-'*50)

        Item = MpgTrade(ID, email, amount, msg, now_time)
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
    import sys

    from gevent import pywsgi
    app.config['DEBUG'] = True
    WebServer = pywsgi.WSGIServer(('0.0.0.0', 5001), app)
    try:
        logging.info('Server STARTED')
        WebServer.serve_forever()
    except KeyboardInterrupt:
        logging.info('Server CLOSED')
        sys.exit()
