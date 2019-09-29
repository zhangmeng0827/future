# -*- coding: UTF-8 -*-
from django.db import models

# Create your models here.
class Goods(models.Model):
    goodsType = models.CharField(max_length=50)
    goodsName = models.CharField(max_length=50)
    goodsPrice = models.DecimalField(decimal_places=2,max_digits=6)
    goodsDescription = models.CharField(max_length=50)
    goodsNum = models.IntegerField(default=0,verbose_name='库存量')
    goodsPicture = models.CharField(max_length=256,verbose_name='商品图片')

class GoodsTypes(models.Model):
    typeName = models.CharField(max_length=256)
    typeIcon = models.CharField(max_length=256,verbose_name='商品类型图标')

#商品订单
class OnsiteOrder(models.Model):
    orderNum = models.CharField(max_length=50,verbose_name='订单号')
    orderTime = models.DateTimeField(auto_now_add=True,verbose_name='下单时间')
    orderUserid = models.CharField(max_length=50,verbose_name='下单人')
    orderGetman = models.CharField(max_length=50,verbose_name='收货人')
    orderSendman = models.CharField(max_length=50,verbose_name='送货人')
    locationSite = models.CharField(max_length=50,verbose_name='场馆地址')
    locationSeat = models.CharField(max_length=50,verbose_name='场馆座位')
    receivingCall = models.CharField(max_length=50,verbose_name='收货电话')
    couponId = models.IntegerField(default='',verbose_name='优惠券id')
    orderTruePay = models.DecimalField(decimal_places=2,max_digits=7,verbose_name='实际支付金额')
    orderPicture = models.CharField(max_length=150,default='http://liulian.szbeacon.com/%E8%BD%AE%E6%92%AD%E7%94%BB%E9%9D%A2_0002_%E7%BB%84-2-%E6%8B%B7%E8%B4%9D.png',verbose_name='收货图片')
    isPay = models.BooleanField(default=0,verbose_name='是否支付')
    isGet = models.BooleanField(default=0,verbose_name='是否送达')
    class Meta:
        verbose_name_plural = '现场配送系统'
        #联合键约束，避免有重名人
        unique_together = ('orderGetman','orderSendman')
    #模型方法
    #判断订单是否送达
    def isSend(self):
        if self.isGet == 0:
            return '<span style:"color:red;">订单未送达</span>'
        else:
            return '<span style:"color:pink;">订单已送达</span>'
    isSend.descripton = '是否送达'
    isSend.flag = True
    #判断订单是否有人接单
    def getOrder(self):
        if self.orderSendman == '':
            return '<span style:"color:red;">未接单</span>'
        else:
            return '<span style:"color:red;">已经接单</span>'
    getOrder.description = '接单'
    getOrder.flag = True
#现场商品订单详情
class OnsiteOrderDetails(models.Model):
    goodsId = models.CharField(max_length=50)
    num = models.IntegerField(default=0)
    name = models.CharField(max_length=50)
    price = models.DecimalField(decimal_places=2,max_digits=7,default=0)
    orderNum = models.CharField(max_length=50,verbose_name='订单号')
    orderForignkey = models.ForeignKey(OnsiteOrder,default=1,on_delete=models.CASCADE)

class VenueAddress(models.Model):
    address = models.CharField(max_length=50)
