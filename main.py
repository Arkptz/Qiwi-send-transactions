import re
import requests
import base64
import random
from requests.adapters import HTTPAdapter, Retry
from requests.auth import HTTPProxyAuth
from fake_useragent import UserAgent
class Qiwi_account():
  def __init__(self, num, password_qiwi, proxy = False) -> None:
    self.proxy = proxy
    self.user_agent = UserAgent().random
    self.number = num
    self.password_qiwi = password_qiwi
    self.session = self.generate_session_authorize()
    self.balance = self.get_balance()
    self.work = False
  def __str__(self):
        return f'Qiwi_account(number={self.number}, balance={self.balance}, work = {self.work})'
  def configure_session(self):
    s = requests.Session()
    if self.proxy:
      proxy_list_elements = self.proxy.split(':')
      proxies = { 
                      "https"  : f"http://{proxy_list_elements[2]}:{proxy_list_elements[3]}@{proxy_list_elements[0].replace(r'http://', '')}:{proxy_list_elements[1]}", 
                      }
      auth = HTTPProxyAuth(proxy_list_elements[2], proxy_list_elements[3])
      s.proxies = proxies
      s.auth = auth
      resp = s.get('https://httpbin.org/ip')
      print(resp.content)
    retries = Retry(total=5,
                backoff_factor=0.1,
                status_forcelist=[ 500, 502, 503, 504 ])
    s.mount('http://', HTTPAdapter(max_retries=retries))
    s.headers['user-agent'] = self.user_agent
    return s
  def generate_session_authorize(self):
    s = self.configure_session()
    data = {
    'token_type':'headtail',
    'grant_type':'password',
    'client_secret':'P0CGsaulvHy9',
    'client_id':'web-qw',
    'username':self.number,
    'password':self.password_qiwi
    }
    resp = s.post('https://qiwi.com/oauth/token', data=data, )
    token = resp.json()['access_token']
    refr_tok = resp.json()['refresh_token']
    token_base64 = 'TokenHeadV2 ' + base64.b64encode(f'web-qw:{token}'.encode('utf-8')).decode('utf-8')
    s.headers['authorization'] = token_base64
    resp = s.post('https://qiwi.com/payment/form/99', data={"extra['account']":self.number})
    sinap_app_id = resp.text.split('SinapSettings:{applicationId:"')[1].split('"')[0]
    sinap_app_secret = resp.text.split(',applicationSecret:"')[1].split('"')[0]
    s.headers['x-application-id'] = sinap_app_id
    s.headers['x-application-secret'] = sinap_app_secret
    s.headers['accept'] = 'application/vnd.qiwi.v2+json'
    self.work = True
    return s
  def get_balance(self):
    resp = self.session.get(f'https://edge.qiwi.com/funding-sources/v2/persons/{self.number}/accounts')
    balance_rub = resp.json()['accounts'][0]['balance']['amount']
    self.balance = balance_rub
    return balance_rub
  def generate_id(self):
      nums = '0123456789'
      id_str = ''
      for i in range(11):
        id_str+=random.choice(nums)
      return id_str
  def transfer_to_qiwi(self, num_transfer, count_rubles):
    data = {
  "id": self.generate_id(),
  "sum": {
    "amount": count_rubles,
    "currency": "643"
  },
  "paymentMethod": {
    "accountId": "643",
    "type": "Account"
  },
  "comment": "",
  "fields": {
    "sinap-form-version": "qw::99, 12",
    "account": f"+{num_transfer}",
    "CHECKOUT_REFERER": "https://qiwi.com/transfer"}
  }
    resp = self.session.post('https://edge.qiwi.com/sinap/api/terms/99/payments', json=data)
    print(resp.json())
    try:
      if resp.json()['transaction']['state']['code'] == 'AwaitingSMSConfirmation':
        id = resp.json()['id']
        txnid = resp.json()['transaction']['id']
        print(id, txnid)
        code = input('Введи код:')
        resp = self.session.post(f'https://edge.qiwi.com/sinap/payments/{id}/confirm', json={'smsCode': code})
        print(resp.text)
        if resp.json()['transaction']['state']['code'] == 'Accepted':
          self.get_balance()
          return 'Success'
    except:
      return 'Not_success'
  def transfer_to_yoomoney(self, num_transfer, count_rubles):
    data = {
  "id": self.generate_id(),
  "sum": {
    "amount": count_rubles,
    "currency": "643"
  },
  "paymentMethod": {
    "accountId": "643",
    "type": "Account"
  },
  "comment": "",
  "fields": {
    "sinap-form-version": "qw::26476, 10",
    "account": f"{num_transfer}"}
  }
    resp = self.session.post('https://edge.qiwi.com/sinap/api/terms/26476/payments', json=data)
    print(resp.json())
    try:
      if resp.json()['transaction']['state']['code'] == 'AwaitingSMSConfirmation':
        id = resp.json()['id']
        txnid = resp.json()['transaction']['id']
        print(id, txnid)
        code = input('Введи код:')
        resp = self.session.post(f'https://edge.qiwi.com/sinap/payments/{id}/confirm', json={'smsCode': code})
        print(resp.text)
        if resp.json()['transaction']['state']['code'] == 'Accepted':
          self.get_balance()
          return 'Success'
    except:
      return 'Not_success'
  def transfer_to_card(self, num_transfer, count_rubles):
    data = {
  "id": self.generate_id(),
  "sum": {
    "amount": count_rubles,
    "currency": "643"
  },
  "paymentMetho d": {
    "accountId": "643",
    "type": "Account"
  },
  "comment": "",
  "fields": {
    "sinap-form-version": "qw::31873, 9",
    "account": f"{num_transfer}",
    "country": "643",
    "rec_country": "Россия"}
  }
    resp = self.session.post('https://edge.qiwi.com/sinap/api/terms/31873/payments', json=data)
    print(resp.json())
    try:
      if resp.json()['transaction']['state']['code'] == 'AwaitingSMSConfirmation':
        id = resp.json()['id']
        txnid = resp.json()['transaction']['id']
        print(id, txnid)
        code = input('Введи код:')
        resp = self.session.post(f'https://edge.qiwi.com/sinap/payments/{id}/confirm', json={'smsCode': code})
        print(resp.text)
        if resp.json()['transaction']['state']['code'] == 'Accepted':
          self.get_balance()
          return 'Success'
    except:
      return 'Not_success'
    




qiwi1 = Qiwi_account('number', 'password')

print(qiwi1)

