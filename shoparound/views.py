# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.decorators.cache import cache_page
from django.db.models import Q
from fanForum.views import *
from .models import *
from .pay import *
from .forpay import *
import datetime
import json
# Create your views here.
def hello(request):
    return HttpResponse('just do it!!!')

#周边产品展示设置缓存
@cache_page(180)
def setAroundGoods(request):
    aroundGoods = AroundGoods.objects.all()
    goodsCache = set()
    objList = []
    for i in aroundGoods:
        #判断该周边产品是否在缓存中
        if i.name not in goodsCache:
            objDict = {}
            objDict['name'] = i.name
            objDict['price'] = i.price
            objDict['mainImg'] = i.mainImg
            #存入商品id
            objDict['id'] = i.id
            objList.append(objDict)
            #将该周边产品名加入缓存中
            goodsCache.add(i.name)
    return JsonResponse({'status':1,'data':objList})

#周边产品展示详情
def showAroundGoods(request):
    goodName = request.POST.get('goodName')
    #筛选出符合条件的对象集
    aroundGoods = AroundGoods.objects.filter(name=goodName)
    sendData = []
    #库存
    sumNumber = 0
    for i in aroundGoods:
        sumNumber += i.storeNum
    #筛选出符合条件的单个对象
    aroundGood = AroundGoods.objects.filter(name=goodName)[0]
    objDict = {}
    objDict['id'] = aroundGood.id
    objDict['name'] = aroundGood.name
    objDict['price'] = aroundGood.price
    objDict['postage'] = aroundGood.postage
    #优惠券
    couponList = []
    #判断优惠券id是否为空
    if aroundGood.canuseCoupon != '':
        coupon = Coupon.objects.get(id=aroundGood.canuseCoupon)
        couponDict = {}
        couponDict['require'] = coupon.require
        couponDict['reduce'] = coupon.reduce
        couponList.append(couponDict)
    objDict['coupon'] = couponList
    objDict['mainImg'] =aroundGood.mainImg
    objDict['imgList'] = (i for i in [aroundGood.imgOne,aroundGood.imgTwo,aroundGood.imgThree] if i != '' )
    objDict['detailImg'] = aroundGood.detailImg
    sendData.append(objDict)
    return JsonResponse({'status':1,'data':sendData})

#获取周边产品的size、color、store列表
def getList(request):
    goodName = request.POST.get('goodName')
    aroundGoods = AroundGoods.objects.filter(name=goodName)
    sizeList = []
    colorList = []
    storeList = []
    objDict = {}
    for aroundGood in aroundGoods:
        if aroundGood.size !=''or aroundGood.color !='':
            if aroundGood.size !='':
                sizeList.append(aroundGood.size)
            if aroundGood.color != '':
                colorList.append(aroundGood.color)
            storeList.append([aroundGood.size,aroundGood.color,aroundGood.storeNum])
            #将商品的size和color作为键，id作为值
            objDict[aroundGood.size+aroundGood.color] = aroundGood.id
    colorList = list(set(colorList))
    sizeList = list(set(sizeList))
    return JsonResponse({'status':1,'colorList':colorList,'sizeList':sizeList,'storeList':storeList,'objDict':objDict})

#获取下单人所有的地址详情
def getAddress(request):
    userid = request.POST.get('userid')
    venueAddress = LocationNote.objects.filter(userid=userid).order_by('-id')
    sendData = []
    for i in venueAddress:
        objDict = {}
        address = i.address.split(',')
        objDict['userid'] = i.userid
        objDict['cosignee'] = i.consignee
        objDict['mobile'] = i.mobile
        objDict['address'] = ''.join(address)
        objDict['isDefault'] = i.isDefault
        objDict['addressDetail'] = i.addressDetail
        objDict['id'] = i.id
        sendData.append(objDict)
    return JsonResponse({'status':1,'data':sendData})

#记录下单人填写的地址
def recordAdress(request):
    userid = request.POST.get('userid')
    consignee = request.POST.get('consignee')
    mobile = request.POST.get('mobile')
    address = request.POST.get('address')
    addressDetail = request.POST.get('addressDetail')
    isDefault = request.POST.get('isDefault')
    #判断是否为默认地址
    if isDefault == 'true':
        isDefault = True
        #筛选isDefault=1的对象集
        theDefault = LocationNote.objects.filter(isDefault=1,userid=userid)
        #如果存在多个isDefault=1的地址，则将其修改为非默认地址
        if theDefault.exists():
            for i in theDefault:
                i.isDefault = 0
                i.save()
    else:
        isDefault = False
    #查询是否有这个地址，没有就根据参数创建。
    LocationNote.objects.get_or_create(userid=userid,consignee=consignee,mobile=mobile,address=address,addressDetail=addressDetail,isDefault=isDefault)
    return JsonResponse({'status':1})

#删除地址
def delAdress(request):
    #获取地址ID
    addressId = request.POST.get('id')
    #查询到该地址
    location = LocationNote.objects.get(int(addressId))
    location.delete()
    return JsonResponse({'status':1})

#编辑地址
def changeAdress(request):
    #获取修改的参数
    userid = request.POST.get('userid')
    consigness = request.POST.get('consigness')
    mobile = request.POST.get('mobile')
    address = request.POST.get('address')
    addressDetail = request.POST.get('addressDetail')
    isDefault = request.POST.get('isDefault')
    addressid = request.POST.get('id')
    #查询被修改的地址
    location = LocationNote.objects.get(int(addressid))
    location.userid = userid
    location.consignee = consigness
    location.mobile = mobile
    location.address = address
    location.addressDetail = addressDetail
    #判断该地址是否为默认地址
    if isDefault == 'true':
        isDefault = True
        theDefault = LocationNote.objects.filter(userid=userid,isDefault=1)
        #判断是否存在多个默认地址
        if theDefault.exists():
            for i in theDefault:
                i.isDefault = 0
                i.save()
    else:
        isDefault = False
    location.isDefault = isDefault
    location.save()
    return  JsonResponse({'status':1})

#获取默认地址
def getDefaultAdress(request):
    userid = request.POST.get('userid')
    locationId = request.POST.get('locationId')
    #判断locationId是否为0
    if locationId == 0:
        #获取默认地址
        location = LocationNote.objects.filter(isDefault=1,userid=userid)
        if location.exists():
            i = location[0]
        #非默认地址
        else:
            location = LocationNote.objects.filter(userid=userid).order_by('-id')
            if location.exists():
                i = location[0]
            else:
                return JsonResponse({'status':0,'data':None})
    else:
        i = LocationNote.objects.get(id=locationId)
    sendData = []
    objDict = {}
    address = i.address.split(',')
    objDict['consignee'] = i.consignee
    objDict['mobile'] = i.mobile
    objDict['address'] = ''.join(address)
    objDict['addressDetail'] = i.addressDetail
    objDict['id'] = i.id
    objDict['isDefault'] = i.isDefault
    sendData.append(objDict)
    return JsonResponse({'status':1,'data':sendData})

#购物车详情
def orderAction(request):
    userid = request.POST.get('userid')
    locationId = request.POST.get('locationId')
    postage = request.POST.get('postage')
    orderTruePay = request.POST.get('orderTruePay')
    message = request.POST.get('message')
    couponPrice = request.POST.get('couponPrice')
    #获取购物车
    goodCar = request.POST.get('goodCar')
    #将json字符串转为Python对象
    goodCar = json.loads(goodCar)
    carList = []
    #将购物车商品信息存入carList
    for i in goodCar:
        objDict = {}
        objDict['goodId'] = i['goodId']
        objDict['goodName'] = i['goodName']
        objDict['goodPrice'] = i['goodPrice']
        objDict['goodNum'] = i['goodNum']
        objDict['goodImg'] = i['goodImg']
        objDict['idforcar'] = i['idforcar']
        carList.append(objDict)
    #创建商品库存字典对象
    returnCode = {}
    #遍历购物车，查询商品库存信息
    for shopCar in carList:
        goodId = int(shopCar['goodId'])
        goodNum = int(shopCar['goodNum'])
        goodName = shopCar['goodName']
        goodType = shopCar['goodType']
        try:
            aroundGoods = AroundGoods.objects.get(id=goodId)
            #如果购物车中商品数量大于库存
            if aroundGoods.storeNum -goodNum < 0:
                returnCode[goodName+'_'+goodType] = '商品'+str(goodName)+'仅'+(aroundGoods.storeNum)+'件'
        except Exception as e:
            returnCode[goodName+'_'+goodType] = '商品'+str(goodName)+'失效'
    #返回错误集
    if len(returnCode) > 0:
        returnError = ''
        for k in returnCode:
            returnError += k + returnCode[k] + ':'
        return JsonResponse({'status':1,'data':returnError})
    #清空购物车
    if carList[0]['idforcar'] != None:
        for car in carList:
            idforcar = car['idforcar']
            car = Association.objects.get(id=idforcar)
            car.isdelete = 1
            car.save()
    #获取客户端IP
    X_FORWARDED = request.META.get('HTTP_X_FORWARDED_FOR')
    #负载均衡部署的IP
    if X_FORWARDED:
        ip = X_FORWARDED.split(',')[0]
    #代理IP
    else:
        ip = request.META.get('REMOTE_ADDR')
    #下单详情存入数据库中
    aroundOrder = AroundOrder()
    aroundOrder.userid = userid
    aroundOrder.orderTime = datetime.datetime.now()
    aroundOrder.locationId = locationId
    aroundOrder.orderTruePay = orderTruePay
    aroundOrder.orderNum = randomNum()
    aroundOrder.postageFee = postage
    aroundOrder.couponReduce = couponPrice
    aroundOrder.message = message
    aroundOrder.save()
    #下单商品详情存入数据库中
    for i in carList:
        aroundOrderDetail = AroundOrderDetail()
        aroundOrderDetail.id = i['id']
        aroundOrderDetail.goodName = i['goodName']
        aroundOrderDetail.goodNum = i['goodNum']
        aroundOrderDetail.goodPrice = i['goodPrice']
        aroundOrderDetail.goodImg = i['goodImg']
        aroundOrderDetail.orrderForeignkey = aroundOrder
        aroundOrderDetail.save()
        goodStr = str(i['goodName']) + '_' + str(i['goodNum']) + '件'
    #调用微信下单接口
    orderNum = randomNum()
    returnData = payAroundOrder(orderNum,ip,orderTruePay,userid)
    #将地址信息返回给前端
    location = LocationNote.objects.get(id=locationId)
    sendData = []
    locationDict = {}
    locationDict['mobile'] = location.mobile
    locationDict['consignee'] = location.consignee
    locationDict['address'] = location.address
    locationDict['addressDeatil'] = location.addressDetail
    locationDict['userid'] = location.userid
    sendData.append(locationDict)
    return JsonResponse({'status':1,'locationData':sendData,'returnFromWx':returnData})

#查询支付状态,并修改商品库存
def queryPayState(request):
    #获取用户下单数据，并将数据转为python对象
    orderData = request.POST.get('orderData')
    orderData = json.loads(orderData)
    #调用微信支付查询接口
    reternData = queryOrderState(orderData)
    #判断是否支付成功，修改商品库存
    if reternData['state'] == 'SUCCESS':
        shopCar = orderData['goodcar']
        for i in shopCar:
            aroundGoods = AroundGoods.objects.get(i['goodId'])
            num = i['goodNum']
            newStoreNum = aroundGoods['storeNum'] - num
            #如果剩余库存小于0则将库存置为0
            if newStoreNum < 0:
                aroundGoods['storeNum'] = 0
            else:
                aroundGoods['storeNum'] = newStoreNum
            aroundGoods.save()
    return JsonResponse(reternData)

#计算购物车中商品数量
def carDetailes(request):
    #获取用户购物车字段
    gooid = request.POST.get('goodid')
    userid = request.POST.get('userid')
    num = request.POST.get('num')
    #获取购物车对象
    shopCar = Association.objects.filter(userid=userid,goodid=gooid)
    #判断购物车是否存在
    if shopCar.exists():
        #获取购物车第一个对象,并判断是否清空购物车
        shopCar = shopCar[0]
        #如果购物车被清空，则数目为被抓取的num数,购物车重新释放
        if shopCar.isdelete == 1:
            shopCar.num = int(num)
            shopCar.isdelete = 0
            shopCar.save()
        #未清空购物车，计算购物车商品数量（此时数量加上已在购物车的数量）
        shopCar.num += int(num)
        shopCar.save()
    #购物车不存在则创建存入数据库
    #创建新的购物车对象
    else:
        shopCar = Association()
        shopCar.goodid = gooid
        shopCar.userid = userid
        shopCar.num = num
        shopCar.save()
    return JsonResponse({'status':1})

#返回购物车详情数据至前端
def showCar(request):
    userid = request.POST.get('userid')
    sendData = []
    #获取未删除的购物车对象
    shopCars = Association.objects.filter(userid=userid,isdelete=0)
    #遍历购物车，并获取购物车中的商品详情
    for shopCar in shopCars:
        goodid = shopCar.goodid
        #捕获异常
        try:
            aroundGoods = AroundGoods.objects.get(id=goodid)
        except:
            #跳出本次循环
            continue
        #判断该商品的库存是否为0
        if aroundGoods.storeNum == 0:
            continue
        #获取该商品详情
        objDict = {}
        objDict['goodName'] = aroundGoods.name
        objDict['storeNum'] = aroundGoods.storeNum
        objDict['goodPrice'] = aroundGoods.price
        objDict['postage'] = aroundGoods.postage
        objDict['goodImg'] = aroundGoods.imgOne
        objDict['color'] = aroundGoods.color
        objDict['size'] = aroundGoods.size
        objDict['goodNum'] = shopCar.num
        objDict['idforcar'] = shopCar.id
        objDict['goodId'] = shopCar.goodid
        #判断是否使用优惠券
        couponList = []
        if aroundGoods.canuseCoupon != '':
            couponDict = {}
            coupon = Coupon.objects.get(id=aroundGoods.canuseCoupon)
            couponDict['require'] = coupon.require
            couponDict['reduce'] = coupon.reduce
            couponList.append(couponDict)
        objDict['coupon'] = couponList
        sendData.append(objDict)
    return JsonResponse({'status':1,'data':sendData})

#清空购物车
def clearCar(request):
    #获取购物车id
    idforcar = int(request.POST.get('idforcar'))
    shopcar = Association.objects.get(id=idforcar)
    shopcar.isdelete = 1
    shopcar.save()
    return JsonResponse({'status':1})

#计算购物车中商品数量
def getNumFromCar(request):
    #获取userid
    userid =request.POST.get('userid')
    #获取该用户未被删除的购物车对象
    shopCars = Association.objects.filter(userid=userid,isdelete=0)
    num = 0
    #遍历购物车对象并计算购物车商品数量
    for shopCar in shopCars:
        goodid = shopCar.goodid
        #捕获异常
        try:
            aroundGood = AroundGoods.objects.get(id=goodid)
        except:
            continue
        if aroundGood.storeNum == 0:
            continue
        num += 1
        shopCar.num = num
        shopCar.save()
    return JsonResponse({'state':1,'num':num})

#获取周边下单详情，并判断交易状态
def getOrederDetails(request):
    userid = request.POST.get('userid')
    orderStatus = request.POST.get('orderStatus')
    sendData = []
     #获取周边下单对象，并判断交易状态
    if orderStatus == 'all':
        aroundOrders = AroundOrder.objects.filter(userid=userid,isDelete=0).order_by('-id')
    else:
        #Q对象查询
        aroundOrders= AroundOrder.objects.filter(Q(userid=userid)&Q(orderStatus=orderStatus)&Q(isDelete=0)).order_by('-id')
    #如果存在满足条件的对象,则获取下单详情
    if aroundOrders.exists():
        #遍历周边下单对象
        for aroundOrder in aroundOrders:
            #反向查询获取下单详情对象
            aroundOrderDetail = aroundOrder.aroundorderdetail_set.all()
            #通过fliter获取下单详情对象
            #aroundOrderDetail = AroundOrderDetail.objects.filter(orrderForeignkey=aroundOrder.id)
            #定义下单详情字典
            aroundOrderDetailDict = {}
            #创建下单详情列表
            aroundOrderDetailList = []
            #定义下单商品数目
            num  = 0
            #遍历下单详情对象，获取下单商品详情
            for goodsCar in aroundOrderDetail:
                #获取下单详情数据
                objDict = {}
                objDict['goodId'] = goodsCar.id
                objDict['goodName'] = goodsCar.goodName
                objDict['goodNum'] = goodsCar.goodNum
                objDict['goodImg'] = goodsCar.goodImg
                objDict['goodPrice'] = goodsCar.goodPrice
                #获取周边商品对象，并获取goodType字段
                aroundGoods = AroundGoods.objects.get(id=goodsCar.id)
                objDict['goodsType'] = aroundGoods.color + aroundGoods.size
                aroundOrderDetailList.append(objDict)
                num += goodsCar.goodNum
            #获取下单总详情
            aroundOrderDetailDict['goodsCar'] = aroundOrderDetailList
            aroundOrderDetailDict['orderTruePay'] = aroundOrder.orderTruePay
            aroundOrderDetailDict['payNum'] = num
            aroundOrderDetailDict['orderNum'] = aroundOrder.orderNum
            aroundOrderDetailDict['id'] = aroundOrder.id
            aroundOrderDetailDict['creatTime'] = aroundOrder.orderTime
            #判断交易类型
            # type传参，all  0-待支付，1-待收货，2-已收货交易完成售后，3-交易关闭
            if aroundOrder.orderStatus == '0':
                #下单时间超过30分钟仍未支付，则交易关闭
                startTime = datetime.datetime.strptime(aroundOrder.orderTime,'%Y-%m-%d %H:%M:%S')
                if time.time() - startTime.timestamp() > 1800:
                    aroundOrder.orderStatus = 3
                    aroundOrder.save()
                    #过期时间
                    aroundOrderDetailDict['expiry_time'] = ''
                    aroundOrderDetailDict['orderStatus'] = 3
                #下单时间未超过30分钟，则返回过期时间以及交易状态
                    #过期时间设置为下单时间+2分钟
                    aroundOrderDetailDict['expiry_time'] = str(startTime+datetime.timedelta(minutes=2))
                    aroundOrderDetailDict['orderStatus'] = 0
            #交易状态为待收货，判断收货时间
            elif aroundOrderDetailDict['orderStatus'] == '1':
                if aroundOrder.receiveTime != '':
                    #收货时间大于7天，则状态置为已收货
                    if time.time() - datetime.datetime.strptime(aroundOrder.receiveTime,'%Y-%m-%d %H:%M:%S').timestamp() > 604800:
                        aroundOrder.orderStatus = 2
                        aroundOrder.save()
                        aroundOrderDetailDict['orderStatus'] = 2
                    else:
                        aroundOrderDetailDict['orderStatus'] = 1
                else:
                    aroundOrderDetailDict['orderStatus'] = 1
                aroundOrderDetailDict['expiry_time'] = ''
            #交易状态为已收货或者交易关闭
            aroundOrderDetailDict['orderStatus'] = aroundOrder.orderStatus
            aroundOrderDetailDict['expiry_time'] = ''
            sendData.append(aroundOrderDetailDict)
    return JsonResponse({'status':1,'data':sendData})

#取消订单
def cancleOrder(request):
    #获取订单id
    id = request.POST.get('id')
    aroundOrder = AroundOrder.objects.get(id=id)
    #交易关闭
    aroundOrder.orderStatus = 3
    aroundOrder.save()
    return JsonResponse({'status':1})

#交易成功后删除订单
def delOrder(request):
    #获取订单id
    id = request.POST.get('id')
    aroundOrder = AroundOrder.objects.get(id=id)
    #删除订单
    aroundOrder.isDelete = 1
    aroundOrder.save()
    return JsonResponse({'status':1})

#确认收货
def confirmOrder(request):
    id = request.POST.get('id')
    aroundOrder = AroundOrder.objects.get(id=id)
    #获取物流信息
    logisticsInfo = aroundOrder.logisticsInfo
    #判断物流信息是否为空
    if logisticsInfo == '':
        #封装收货信息
        logisticsInfo = json.dumps([{'acceptime':'','accepadress':'','remark':'已确认收货'}])
        aroundOrder.logisticsInfo = logisticsInfo
    aroundOrder.save()
    return JsonResponse({'status':1})

#获取周边下单详情，并判断交易状态
def showOrder(request):
    id = request.POST.get('id')
    #获取周边订单对象
    aroundOrder = AroundOrder.objects.get(id=id)
    orderStatus = aroundOrder.orderStatus
    #反向查询获取周边订单详情对象（两个表是一对多的关系）
    #aroundOrderDetail = aroundOrder.aroundorderdetail_set.all()
    #用filter正向查询获取周边订单详情对象
    aroundOrderDetail = AroundOrderDetail.objects.filter(orrderForeignkey=aroundOrder.id)
    #创建订单详情列表
    orderDict = {}
    #创建商品详情列表
    goodsDetailList = []
    #定义订单交易商品数量
    payNum = 0
    #遍历周边订单详情对象，获取每个商品的详情
    for goodsDetail in aroundOrderDetail:
        objDict = {}
        objDict['goodId'] = goodsDetail.goodId
        objDict['goodName'] = goodsDetail.goodName
        objDict['goodImg'] = goodsDetail.goodImg
        objDict['goodPrice'] = goodsDetail.goodPrice
        objDict['goodNum'] = goodsDetail.goodNum
        payNum += goodsDetail.goodNum
        #获取周边商品对象
        aroundGood = AroundGoods.objects.get(id=id)
        objDict['goodsType'] = str(aroundGood.color) + str(aroundGood.size)
        goodsDetailList.append(objDict)
    #获取订单详情数据
    orderDict['goodsDetail'] = goodsDetailList
    orderDict['orderStatus'] = orderStatus
    orderDict['payNum'] = payNum
    orderDict['orderTruePay'] = aroundOrder.orderTruePay
    orderDict['orderTime'] = aroundOrder.orderTime
    orderDict['payTime'] = aroundOrder.payTime
    orderDict['message'] = aroundOrder.message
    orderDict['postageFee'] = aroundOrder.postageFee
    orderDict['cuponReduce'] = aroundOrder.couponReduce
    #获取订单地址
    #根据地址ID,获取订单地址对象
    location = LocationNote.objects.get(id=aroundOrder.locationId)
    orderDict['location'] = toDict(location)
    #判断交易状态
    # type传参，all  0-待支付，1-待收货，2-已收货交易完成售后，3-交易关闭
    if orderStatus == '0':
        #订单超过30分钟未支付，则交易关闭
        #格式化收货时间
        orderTime = datetime.datetime.strptime(aroundOrder.orderTime,'%Y-%m-%d %H:%M:%S')
        if time.time() - orderTime.timestamp() > 1800:
            aroundOrder.orderStatus = 3
            aroundOrder.save()
            #过期时间为空
            orderDict['expireTime'] = ''
        #未超过30分钟，则设置过期时间（下单时间+15分钟）
        orderDict['expireTime'] = str(orderTime+datetime.timedelta(minutes=15))
    elif orderStatus == '1':
        #过期时间为空
        orderDict['expireTime'] = ''
        #存在物流信息
        if aroundOrder.logisticsInfo != '':
            #转为python对象的json字符串
            logisticsInfo = json.loads(aroundOrder.logisticsInfo)
            routeList = logisticsInfo
        else:
            #不存在物流信息，则调用丰桥接口查询
            xml = rootXml(aroundOrder.waybillId)
            routeList = queryRoot(xml)[1:]
        #返回物流信息（存在物流信息则返回，不存在则返回待揽件）
        orderDict['logisticsInfo'] = [{'accpetTime':'','acceptAddress':'','remark':'待顺丰网点揽件'}] if len(routeList) == 0 else routeList
        #根据操作码，判断是否收货
        if orderDict['logisticsInfo'][-1]['acceptTime'] != '':
            #创建操作码列表
            opcode = []
            #遍历路由字典
            for code in routeList:
                opcode.append(code['opcode'])
            #操作码存在80，则表明已收货
            if '80' in opcode:
                receive = routeList[-1]['accpetTime']
                now = time.time()
                #格式化时间
                receiveTime = datetime.datetime.strptime(receive,'%Y-%m-%d %H:%M:%S').timestamp()
                #存储物流信息以及收货时间
                aroundOrder.logisticsInfo = json.dumps(routeList)
                aroundOrder.receiveTime = receive
                #收货时间大于7天，交易状态为已收货
                if now - receiveTime > 64800:
                    aroundOrder.orderStatus = 2
                aroundOrder.save()
    elif aroundOrder.orderStatus == '2':
        orderDict['expireTime'] = ''
        orderDict['logisticsInfo'] = aroundOrder.logisticsInfo
    else:
        orderDict['expireTime'] = ''
        orderDict['logisticsInfo'] = ''
    return JsonResponse({'status':1,'data':orderDict})

#重新发起支付
def rePay(request):
    #获取关闭订单的订单号以及购物车商品信息(转为python对象的json字符串)
    oldOrderNum = request.POST.get('orderNum')
    carList = request.POST.get('car_list')
    carList = json.loads(carList)
    goodStr = ''
    #遍历购物车，获取商品留言
    for goodDetail in carList:
        goodStr = goodDetail['goodsName'] + 'X' + str(goodDetail['goodsNum']) + ','
    #获取周边下单对象
    aroundOrder = AroundOrder.objects.get(orderNum=oldOrderNum)
    #调用微信关闭订单接口
    returnData = closeOrder(oldOrderNum)
    if returnData['result_code'] == 'FAIL':
        return JsonResponse({'status':1,'data':'订单关闭失败'})
    #重新发起支付，获取客户端IP
    x_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_ip:
        ip = x_ip.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    #获取新的订单号
    newOrderNum = randomNum()
    #发起支付请求
    data = payAroundOrder(ip,newOrderNum,str(aroundOrder.orderTruePay),aroundOrder.userid)
    #获取地址对象
    location = LocationNote.objects.get(id=aroundOrder.locationId)
    orderData = {}
    #获取订单详情
    orderData['orderTruePay'] = aroundOrder.orderTruePay
    orderData['orderNum'] = aroundOrder.orderNum
    orderData['newOrderNum'] = newOrderNum
    orderData['orderPhone'] = location.mobile
    #获取地址（省、市、区）
    locationList = location.region.split(',')
    orderData['d_province'] = locationList[0]
    orderData['d_city'] = locationList[1]
    orderData['d_county'] = locationList[2]
    #获取具体地址
    orderData['d_address'] = LocationNote.addressDetail
    #获取购买商品留言
    orderData['good_str'] = goodStr + '留言' + aroundOrder.message
    #获取商品具体详情
    orderData['carList'] = carList

    return JsonResponse({'status':1,'data':data,'sendData':orderData})





















