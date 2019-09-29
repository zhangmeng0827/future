# -*- coding: utf-8 -*-
import json

import requests

#获取access_token
# https请求方式: GET
# https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET
from customer.WXBizDataCrypt import WXBizDataCrypt

def get_access_token():
    id = 'wx16360426dc864b7d'
    secret = '1d0e23ca07aa746e09c774b2140d67a6'
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'%(id,secret)
    respone = requests.get(url).text
    access_token =  json.loads(respone).get("access_token")
    return  access_token

#小程序通过code获取
# openid	string	用户唯一标识
# session_key	string	会话密钥
# unionid	string	用户在开放平台的唯一标识符，在满足 UnionID 下发条件的情况下会返回，详见 UnionID 机制说明。
def get_unionid(code):
    appid = "wx16360426dc864b7d"
    secret = "1d0e23ca07aa746e09c774b2140d67a6"
    js_code = code
    url = "https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={js_code}&grant_type=authorization_code".format(appid=appid, secret=secret, js_code=js_code)

    response = requests.get(url)
    text = response.text
    d = json.loads(text)

    return d

#解析，获取用户信息
def getuserdata(sessionKey,encryptedData,iv):
    appId = 'wx16360426dc864b7d'
    # encryptedData="/YLgT51kYs/1bhzRVslIKptLtcuhiskzqPIhCvaUfLKF2f87ICh1vtS6SK99wkJDKe6zJOWIxVP7kgZLJ4jIcr1pE/LAqN/Menoj0rcnQRezRWgv9bu4RXZqC032sqxYwDU+dQz/hZkQLHXySeEAmy+TN8EPhy8EndKHO+hjXqdUCdydlT38mVukfP5iUGjNidowlChXGyE/ehoz+c0YutQoPt880FWzqxP4UoAMYn6MirBk72bx9w0TVAnag0jBeCIhg7eLS51ZfFGNFtxb1L0hVuRwR4zUq3pcdvYdeKmTLVlpZIAaqgpJQUlPLSBx6fz+Ty15pYM837jUOaVBfTvA/pACt21nA4PhGCny+u6QmRg7GgzLdwwsYBGi2bs+KJ2IhZK6eclqqmct43mlqijthQr9sFlwyU2oMfRy9w+X4aqLEUgwXm1t1HwvTr7nHU/MGHF7lFNvj9PvbNzELZ3RTXBSuOsmNGmeKOMOI8AunJqsDqchth+elUcVGGPuWxI5nH4vwRE0y78yyWlvCg=="
    # iv="91drFoVhiGdGtXAEXi0K6Q=="
    pc = WXBizDataCrypt(appId, sessionKey)
    data = pc.decrypt(encryptedData, iv)
    return  data

if __name__ == '__main__':
    pass


