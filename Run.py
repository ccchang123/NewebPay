import hashlib
import json
import re
from datetime import datetime
from threading import Thread
from time import sleep

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from flask import Flask, render_template, request
from rcon.source import Client

app = Flask('', template_folder='', static_folder='')
FORMAT = '%Y-%m-%d, %H:%M:%S'
KEY = 'GtP4kEan9gtgMtRhZhXlZWzbKWqVzwHU'
IV = 'CRE3Cy0Luln13E1P'
ID = 'MS143865933'

with open('log.json', 'r', encoding = 'utf-8') as f:
    log = json.load(f)

class Rcon:
    def __init__(self, ip: str, port: int, password: str) -> None:
        self.ip = ip
        self.port = port
        self.password = password

    def run_command(self, *command: str) -> None:
        try:
            with Client(self.ip, self.port, passwd = self.password) as client:
                for cmd in command:
                    response = client.run(cmd)
                    print(response)
        except ConnectionRefusedError:
            print('連線失敗')

class MpgTrade:
    def __init__(self, MerchantID: str, Email: str, Amount: int, Msg: str, Time: str) -> None:
        self.MerchantID = MerchantID
        self.Email = Email
        self.Amount = Amount
        self.Msg = Msg
        self.Time = Time

    def Encode_Aes(self) -> str:
        TradeInfo = {
            'MerchantID': self.MerchantID,
            'RespondType': 'JSON',
            'TimeStamp': self.Time,
            'Version': '1.5',
            'MerchantOrderNo': self.Time,
            'Amt': self.Amount,
            'ItemDesc': '伺服器贊助',
            'Email': self.Email,
            'OrderComment': self.Msg,
            'ClientBackURL': 'http://ccchang.ddns.net:30003/',
            'CustomerURL': 'http://ccchang.ddns.net:30003/end_buy',
            'EmailModify': 0
        }
        Aes_code = ''
        for i in TradeInfo:
            Aes_code += f'{i}={TradeInfo[i]}&'
        Aes_code = Aes_code[0:-1]
        Aes_code = re.sub(' ', '+', Aes_code)
        Aes_code = re.sub('@', '%40', Aes_code)
        cryptor = AES.new(KEY.encode('utf-8'), AES.MODE_CBC, IV.encode('utf-8'))
        Aes_code = cryptor.encrypt(pad(Aes_code.encode('utf-8'), AES.block_size)).hex()
        self.Aes_code = Aes_code

        return Aes_code

    def Encode_Sha(self) -> str:
        Sha_code = f'HashKey={KEY}&{self.Aes_code}&HashIV={IV}'
        Sha_code = hashlib.sha256(Sha_code.encode('utf-8')).hexdigest().upper()

        return Sha_code

def time():
    last_time = datetime.strptime('1970-01-01, 00:00:00', FORMAT)
    now_time = datetime.strptime(datetime.now().strftime(FORMAT), FORMAT)
    return ((now_time - last_time).total_seconds())

@app.route('/')
@app.route('/index.html')
def main():
    return render_template('index.html')

@app.route('/end_buy', methods=['POST'])
def end_buy():
    print(request.form)
    return render_template('html/end_buy.html')

@app.route('/check', methods=['POST'])
def check():
    global log
    auth_data = {
            'secret': '6LdSC14hAAAAAJD8CX7IWrnwETwTMK_Eks46JcKf',
            'response': request.form['g-recaptcha-response']
    }
    auth_result = requests.post('https://www.google.com/recaptcha/api/siteverify', data=auth_data)
    id_result = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{request.form["minecraft_id"]}').text
    
    if auth_result.json()['success'] and id_result: 
        minecraft_id = request.form['minecraft_id']
        email = request.form['email']
        amount = int(request.form['amount'])
        msg = request.form['msg']
        now_time = str(time())[0:-2]

        log[now_time] = {
            'TimeStamp': now_time,
            'MinecraftID': minecraft_id,
            'Amount': amount,
            'Email': email,
            'Messenge': msg
        }
        with open('log.json', 'w', encoding = 'utf-8') as f:
            json.dump(log, f, indent = 4)

        Item = MpgTrade(ID, email, amount, msg, now_time)

        server = Thread(target=check_pay, args=[now_time, amount])
        server.daemon = True
        server.start()

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
    elif not id_result:
        return render_template('index.html', error_code='無效的遊戲ID')
    else:
        return render_template('index.html', error_code='驗證失敗')

def check_pay(order_no, amount):
    global log
    while True:
        value = f'IV={IV}&Amt={amount}&MerchantID={ID}&MerchantOrderNo={order_no}&Key={KEY}'
        value = hashlib.sha256(value.encode('utf-8')).hexdigest().upper()
        data = {
            'MerchantID': ID,
            'Version': '1.3',
            'RespondType': 'JSON',
            'CheckValue': value,
            'TimeStamp': str(time())[0:-2],
            'MerchantOrderNo': order_no,
            'Amt': amount
        }
        pay_stat = requests.post('https://ccore.newebpay.com/API/QueryTradeInfo', data=data).json()
        if pay_stat['Status'] == 'SUCCESS':
            match pay_stat['Result']['TradeStatus']:
                case '0':
                    print('未付款')
                case '1':
                    print('付款成功')
                    del log[pay_stat['Result']['MerchantOrderNo']]
                    with open('log.json', 'w', encoding = 'utf-8') as f:
                        json.dump(log, f, indent = 4)
                    """ connect = Rcon('127.0.0.1', 25575, '12345')
                    connect.run_command('op cc_chang', 'op cc_chang') """
                    break
                case '3':
                    print('取消付款')
                    break
        sleep(5)

if __name__ == "__main__":
    import sys

    from gevent import pywsgi
    app.config['DEBUG'] = True
    WebServer = pywsgi.WSGIServer(('0.0.0.0', 5001), app)

    if log:
        for i in log:
            print(i, log[i]['Amount'])
            server = Thread(target=check_pay, args=[i, log[i]['Amount']])
            server.daemon = True
            server.start()
    try:
        WebServer.serve_forever()
    except KeyboardInterrupt:
        sys.exit()