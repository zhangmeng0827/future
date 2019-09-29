# -*- coding: UTF-8 -*-
import hashlib
import random
from bs4 import BeautifulSoup
#生成随机字符串(订单号)
def randomNum():
    str = '1234567890QWERTYUIOPASDFGHJKLZXCVBNM'
    astr = ''
    for i in range(26):
        astr += random.choice(str)
    return ''.join(astr)

def getSign(dataDict, key):
    # 签名函数，参数为签名的数据和密钥
    params_list = sorted(dataDict.items(), key=lambda e: e[0], reverse=False)
    params_str = "&".join(u"{}={}".format(k, v) for k, v in params_list) + '&key=' + key
    # 组织参数字符串并在末尾添加商户交易密钥
    md5 = hashlib.md5()  # 使用MD5加密模式
    md5.update(params_str.encode('utf-8'))  # 将参数字符串传入
    sign = md5.hexdigest().upper()  # 完成加密并转为大写
    return sign

# 字典转XML的函数
def dictToXml(dataDict):
    data_xml = []
    for k in sorted(dataDict.keys()):  # 遍历字典排序后的key
        v = dataDict.get(k)  # 取出字典中key对应的value
        if k == 'detail' and not v.startswith('<![CDATA['):  # 添加XML标记
            v = '<![CDATA[{}]]>'.format(v)
        data_xml.append('<{key}>{value}</{key}>'.format(key=k, value=v))
    return '<xml>{}</xml>'.format(''.join(data_xml)).encode('utf-8')  # 返回XML，并转成utf-8，解决中文的问题

#xml转字典
def xmlToDict(dataXml,findlabel='xml'):
    soup = BeautifulSoup(dataXml, features='xml')
    xml = soup.find(findlabel)  # 解析XML
    if not xml:
        return {}
    dataDict = dict([(item.name, item.text) for item in xml.find_all()])
    return dataDict