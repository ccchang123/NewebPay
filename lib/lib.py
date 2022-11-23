import hashlib
import logging
import re

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from rcon.source import Client

from Setting import *

class Rcon():
    def __init__(self) -> None:
        self.__ip = IP
        self.__port = RCON_PORT
        self.__password = PASSWORD

    def run_command(self, command: str) -> str:
        try:
            with Client(self.__ip, self.__port, passwd = self.__password) as client:
                logging.info(f'Run command: {command}')
                return client.run(command)
        except ConnectionRefusedError:
            logging.warning(f'Fail to run command: {command}')
            return '連線失敗'

class MpgTrade:
    def __init__(self, Email: str, Amount: int, Msg: str, Time: str) -> None:
        self.MerchantID = ID
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
            'ClientBackURL': 'https://pay.cocobeen.net',
            'NotifyURL': 'http://203.204.89.217/end_buy',
            'EmailModify': 0,
            'TradeLimit': 180,
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