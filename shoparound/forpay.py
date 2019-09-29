# -*- coding: UTF-8 -*-
import datetime
import os
import time
from django.http import JsonResponse

from shoparound.forfengqiao import *
from shoparound.models import AroundOrder

#微信支付统一下单接口
from shoparound.pay import *

#微信支付统一下单接口
url = "https://api.mch.weixin.qq.com/pay/unifiedorder" #调用地址
appid =	'wx16360426dc864b7d'  #小程序ID
mch_id = '1537642871'         #商户ID
trade_type = 'JSAPI'          #交易类型
#证书以及密钥
key = '1234567890QWERTYUIOPASDFGHJKLZXC'
clientCode = 'LLYLKJSZ'
checkWord = 'STGuVhBlDznxZbvyFFSxP5fdsyH8geFq'
"""
可变参数
body = 'test' #类目
out_trade_no = '20191210' #商户订单号
total_fee = 88 #支付金额，单位分
spbill_create_ip = '14.23.150.211'  #终端ip
notify_url = 'https://www.jianshu.com/p/40c7bd9388a6'  #通知回调url
"""
#封装 请求参数字典
def getParams(body,out_trade_no,total_fee,spbill_create_ip,openid,notify_url):
    dataParams = {
        'appid':appid,
        'mch_id':mch_id,
        'body':body,
        'out_trade_no':out_trade_no,
        'total_fee':total_fee,
        'spbill_create_ip':spbill_create_ip,
        'trade_type':trade_type,
        'notify_url':notify_url,
        'nonce_str':randomNum(),
        'openid':openid
    }
    return dataParams

#获取带有sign的请求参数xml
def getXmlParams(dataParams,key):
    sign = getSign(dataParams, key)
    dataParams['sign'] = sign
    xmlParams = dictToXml(dataParams)
    return xmlParams

#调用微信支付接口发起请求，将响应内容转为字典
def payWx(xmlParams):
    response = requests.post(url=url,data=xmlParams)
    getDict = xmlToDict(response.text)
    return getDict

#查询订单支付状态，并将物流信息存入数据库
def queryOrderState(objDict):
    #获取订单号
    if objDict.get('new_order_num') != '':
        orderNum = objDict.get('new_order_num')
    else:
        orderNum = objDict.get('order_num')
    #封装 请求参数
    params = {
        'appid':appid,
        'mch_id':mch_id,
        'out_trade_no':orderNum,
        'nonce_str':randomNum(),
    }
    #获取签名sign,并转为xml
    sign = getSign(params,key)
    params['sign'] = sign
    xmlParams = dictToXml(params)
    #调用微信订单查询接口,并将响应内容转为字典
    url = 'https://api.mch.weixin.qq.com/pay/orderquery'
    res = requests.post(url=url,data={'xml':xmlParams})
    resDict = xmlToDict(res)
    state = resDict['state']
    #判断支付状态，成功支付则生成物流订单
    if state == 'SUCCESS':
        #当前日期加一天
        sendTime = str(datetime.datetime.now()+datetime.timedelta(days=1))[:10]
        objDict['sendTime'] = sendTime
        #封装 请求参数，调用物流生成订单接口
        xml = requestXml(objDict)
        resDict = addOrders(xml)
        #获取顺丰运单号
        try:
            mailno = resDict['mailno']
        except:
            # 查询物流状态
            orderStateData = checkOrders(objDict['orderNum'])
            mailno = orderStateData['mailno']
            #存储下单人信息
        order = AroundOrder.objects.get(orderNum=objDict['orderNum'])
        order.waybillId = mailno
        order.orderNum = orderNum
        order.payTime = str(datetime.datetime.now())[:-7]
        order.orderStatus = 1
        order.ispay = 1
        order.save()
        #存储物流订单文件至服务器
        orderTxt = """{
        "consignerAddress": "%s",
        "consignerCity": "%s",
        "consignerCounty": "%s",
        "consignerName": "%s",
        "consignerProvince": "%s",
        "consignerTel": "%s",
        "deliverAddress": "T-Park深港影视创意园708",
        "deliverCity": "深圳市",
        "deliverCompany": "榴莲音乐科技（深圳）有限公司",
        "deliverCounty": "福田区",
        "deliverMobile": "0755-26806888",
        "deliverName": "张先生",
        "deliverProvince": "广东省",
        "deliverTel": "0755-26806888",
        "encryptCustName": "true",
        "encryptMobile": "true",
        "expressType": "2",
        "mailNo": "%s", 
        "mainRemark": "%s",
        "monthAccount": "7550069706",
        "payMethod": "1",
        "rlsInfoDtoList": [{
            "twoDimensionCode": "MMM={'k1':'755WE','k2':'021WT','k3':'','k4':'T4','k5':'SF7551234567890','k6':''}",
            "abFlag": "A",
            "codingMapping": "F33",
            "codingMappingOut": "1A",
            "destRouteLabel": "755WE-571A3",
            "proCode": "T6", 
            "sourceTransferCode": "021WTF",
            "waybillNo": "%s",
            "xbFlag": "XB"
        }],
        "zipCode": "755"}
        """%(objDict['d_address'],objDict['city'],objDict['county'],objDict['getman'],objDict['d_province'],
                   objDict['orderPhone'],mailno,objDict['goodName'],mailno)
        #物流信息文件夹路径（以下单时间为文件名后缀）
        saveDirPath = r'/home/zhou/zhoubianorder/%s'%(order.orderTime)[:10]
        #子文件路径
        saveTxtPath = r'/home/zhou/zhoubianorder/%s/%s.txt'%(order.orderTime[:10],mailno)
        #判断是否已创建该文件夹
        if os.path.exists(saveDirPath) == False:
            os.mkdir(saveDirPath)
        #将订单信息写入文件夹
        with open(saveTxtPath,'w') as fp:
            fp.write(orderTxt)
        return {'state':1,'data':'SUCCESS'}
    else:
        return {'state':0,'data':state}

#关闭订单(微信，丰桥)
def closeOrder(orderNum):
    params = {
        'appid':appid,
        'mach_id':mch_id,
        'out_trade_no':orderNum,
        'nonce_str':randomNum()
    }
    sign = getSign(params,key)
    params['sign'] = sign
    xmlParams = dictToXml(params)
    #调用微信关闭订单接口
    url = 'https://api.mch.weixin.qq.com/pay/closeorder'
    code = getVerifyCode(xmlParams)
    res = requests.post(url=url,data={'data':xmlParams,'code':code})
    resDict = resToDict(res.text)
    #调用丰桥物流取消订单接口
    xml = delRequestXml(orderNum)
    delOrders(xml)
    return resDict

#调用微信支付接口下单
def payAroundOrder(ip,orderNum,orderTruePay,ordrUserid):
    #封装请求参数
    body = 'test'
    out_trade_no = orderNum
    total_fee = orderTruePay
    spbill_create_ip = ip
    # 支付后的通知回调url
    notify_url = 'https://www.jianshu.com/p/40c7bd9388a6'
    #统一封装请求参数，并转为xml
    params = getParams(body,out_trade_no,total_fee,spbill_create_ip,ordrUserid[:-3],notify_url)
    xmlParams = getXmlParams(params,key)
    #调用微信支付接口，获取响应字典
    resDict = payWx(xmlParams)
    #解析响应字典
    sendData = {}
    timeStamp = str(int(time.time()))
    sendData['timeStamp'] = timeStamp
    sendData['appId'] = resDict['appid']
    sendData['signType'] = 'MD5'
    sendData['nonce_str'] = resDict['nonce_str'].upper()
    #预支付交易会话标识(用于后续接口调用中使用，该值有效期为2小时)
    sendData['package'] = 'prepay_id='+str(resDict['prepay_id'])
    #微信返回的签名值
    sign = getSign(sendData,key)
    sendData['sign'] = sign
    #下单的订单号
    sendData['order_num'] = orderNum
    return sendData

#订单待支付后重新发起支付
def renewPay(request):
    #获取待支付订单数据
    orderData = request.POST.get('order_data')
    #调用微信关闭订单接口
    orderNum = orderData['orderNum']
    resDict = closeOrder(orderNum)
    #判断订单关闭是否失败
    if resDict['result_code'] == 'FAIL':
        return JsonResponse({'state':0,'data':'订单关闭失败'})
    #重新调用微信支付接口
    #获取客户端ip
    x_FORWARDED_FOR = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_FORWARDED_FOR:
        ip = x_FORWARDED_FOR.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    #获取请求参数
    body = 'test'
    out_trade_no = orderNum
    total_fee = int(float(resDict['orderTruePay']*100))
    spbill_create_ip = ip
    orderUserId = resDict['orderUserId']
    url = 'https://www.jianshu.com/p/40c7bd9388a6'
    #封装请求参数，并转为xml
    params = getParams(body,out_trade_no,total_fee,spbill_create_ip,orderUserId[:-3],url)
    xmlparams = getXmlParams(params,key)
    #发起请求
    resData = payWx(xmlparams)
    #解析响应字典
    sendData = {}
    timeStamp = str(int(time.time()))
    sendData['timeStamp'] = timeStamp
    sendData['appId'] = resData['appid']
    sendData['nonce_str'] = resData['nonce_str'].upper
    sendData['package'] = 'prepay_id='+resData['prepay_id']
    #获取签名
    sign = getSign(sendData,key)
    sendData['sign'] = sign
    #获取订单号
    sendData['order_num'] = orderNum

    return JsonResponse({'state':1,'data':sendData,'orderData':orderData})


















#关闭订单


#向微信下单支付



#待支付再次调用支付









