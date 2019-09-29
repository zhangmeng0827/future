# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .pay import *
from .models import *
from fanForum.views import *
import requests
import datetime,time
import json
# Create your views here.
def hello(request):
    return HttpResponse('just do it!!!')

#微信支付统一下单接口
url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
appid =	'wx16360426dc864b7d'  #小程序ID
mch_id = '1537642871'         #商户ID
trade_type = 'JSAPI'          #交易类型
#证书秘钥
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
#获取请求参数字典
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

#调用支付接口发起请求，将返回内容转为字典
def payWx(xmlParams):
    response = requests.post(url=url,data=xmlParams)
    getDict = xmlToDict(response.text)
    return getDict

#新的现场商品
def newGoods(request):
    goods = Goods.objects.all()
    types = GoodsTypes.objects.all()
    typeContent = []
    for type in types:
        objDict = {}
        objDict['id'] = type.id
        objDict['typeName'] = type.typeName
        objDict['typeIcon'] = type.typeIcon
        objDict['color'] = '#6e6d6d'
        typeContent.append(objDict)
    sendData = {}
    for good in goods:
        goodType = good.goodsType
        if goodType in sendData:
            typeDict = sendData[goodType]
            funcDict = {}
            funcDict['id'] = good.id
            funcDict['goodsName'] = good.goodsName
            funcDict['goodsPrice'] = good.goodsPrice
            funcDict['goodsPicture'] = good.goodsPicture
            funcDict['goodsType'] = goodType
            funcDict['goodsDesctription'] = good.goodsDescription
            funcDict['goodsNum'] = good.goodsNum
            typeDict['id'] = funcDict
        else:
            typeDict = {}
            funcDict = {}
            funcDict['id'] = good.id
            funcDict['goodsName'] = good.goodsName
            funcDict['goodsPrice'] = good.goodsPrice
            funcDict['goodsPicture'] = good.goodsPicture
            funcDict['goodsType'] = goodType
            funcDict['goodsDesctription'] = good.goodsDescription
            funcDict['goodsNum'] = good.goodsNum
            typeDict['id'] = funcDict
            sendData['type'] = typeDict
    return  JsonResponse({'status':1,'data':sendData})

#现场服务下单
def onSiteOrder(request):
    orderNum = randomNum()
    orderUserid = request.POST.get('orderUserid')
    orderGetman = request.POST.get('orderGetman')
    locationSite = request.POST.get('locationSite')
    locationSeat = request.POST.get('locationSeat')
    receivingCall = request.POST.get('receivingCall')
    couponId = request.POST.get('couponID')
    orderTruePay = request.POST.get('orderTruePay')
    goodbag = request.POST.get('goodbag')
    goodbag = json.loads(goodbag)
    #获取部署了nginx的IP
    x_forwarder_for = request.META.get('x_forwarder_for')
    if x_forwarder_for:
        ip = x_forwarder_for.split(',')[0]
    #获取代理服务器IP
    else:
        ip = request.META.get('REMOTE_ADDR')
    #将下单人信息存入数据库
    order = OnsiteOrder()
    order.orderNum = orderNum
    order.orderUserid = orderUserid
    order.orderGetman = orderGetman
    order.locationSite = locationSite
    order.locationSeat = locationSeat
    order.receivingCall = receivingCall
    order.couponId = 0 if couponId =='' else int(couponId)
    order.orderTime = str(datetime.datetime.now())[:-7]
    order.orderTruePay = orderTruePay
    order.save()
    #将下单商品详情存入数据库
    for goodid in goodbag:
        orderDetails = OnsiteOrderDetails()
        orderDetails.goodsId = goodbag[goodid]['goodid']
        orderDetails.name = goodbag[goodid]['name']
        orderDetails.num = goodbag[goodid]['num']
        orderDetails.price = goodbag[goodid]['price']
        orderDetails.orderForignkey = order
        orderDetails.save()
    #将用完后的优惠券删除
        pass
    #包装参数，调用微信支付接口
    body = 'test'  # 类目
    out_trade_no = orderNum # 商户订单号
    total_fee = int(float(orderTruePay)*100)  # 支付金额，单位分
    spbill_create_ip = ip  # 终端ip
    notify_url = 'https://www.jianshu.com/p/40c7bd9388a6'  # 通知回调url
    #包装请求参数，获取返回内容
    dataParms = getParams(body,out_trade_no,total_fee,spbill_create_ip,notify_url,orderUserid[:-3])
    xmlParams = getXmlParams(dataParms,key)
    responseDict = payWx(xmlParams)
    #将返回内容返回给前端
    sendData = {}
    sendData['appid'] = responseDict['appid']
    sendData['prepay_id'] = responseDict['prepay_id']
    sendData['time'] = str(int(time.time()))
    sendData['orderNum'] = orderNum
    sendData['sign_type'] = 'MD5'
    sendData['nonceStr'] = responseDict['nonce_str'].upper()
    sign = getSign(sendData,key)
    sendData['sign'] = sign
    return JsonResponse({'status':1,'data':sendData})

#调用订单查询接口，查询订单支付状态
def queryOrder(request):
    orderNum = request.POST.get('orderNum')
    params = {
        'appid':appid,
        'mch_id':mch_id,
        'out_trade_no':orderNum,
        'nonce_str':randomNum()
    }
    sign = getSign(params,key)
    params['sign'] = sign
    xmlParams = dictToXml(params)
    #接口url
    url = 'https://api.mch.weixin.qq.com/pay/orderquery'
    res = requests.post(url,data=xmlParams)
    #获取返回的内容
    getResDict = xmlToDict(res.text)
    #判断是否是否成功
    if getResDict['result_code'] == 'SUCCESS':
        status= getResDict['trade_state']
        if status == 'SUCCESS':
            trade = OnsiteOrder.objects.get(orderNum=orderNum)
            trade.isPay = 1
            return JsonResponse({'status':1,'code':'SUCCESS'})
        else:
            return JsonResponse({'status':0,'code':'FAIL'})
    else:
        return JsonResponse({'status':0,'code':'FAIL'})

#现场商品订单详情展示
def showOrder(request):
    userid = request.POST.get('userid')
    orders = OnsiteOrder.objects.filter(orderUserid=userid,isPay=1).order_by('-id')
    wait = []
    get = []
    for order in orders:
        orderDict = toDict(order)
        orderNum = orderDict['orderNum']
        #获取订单详情对象
        details = OnsiteOrderDetails.objects.filter(orderNum=orderNum)
        detailList= []
        for detail in details:
            objDict = {}
            objDict['num'] = detail['num']
            objDict['name'] = detail['name']
            objDict['price'] = detail['price']
            detailList.append(objDict)
            orderDict['detailList'] = detailList
        sumPay = 0
        for theOrder in detailList:
            sumPay += theOrder['num']*theOrder['price']
        orderDict['coupon'] = sumPay-orderDict['orderTruePay']
        orderDict['sumPay'] = sumPay
        if orderDict['isGet'] == 0:
            wait.append(orderDict)
        else:
            get.append(orderDict)
    return JsonResponse({'isWait':wait,'isGet':get})
#现场地址
def locationOnsite(request):
    location = VenueAddress.objects.all()
    locationData = []
    for i in location:
        locationData.append(i.address)
    return JsonResponse({'status':1,'data':locationData})















