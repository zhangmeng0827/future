# -*- coding: UTF-8 -*-
from django.db import models

# Create your models here.
#周边产品
class AroundGoods(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(decimal_places=2,max_digits=7)
    postage = models.IntegerField(default=0,verbose_name='邮费')
    mainImg = models.CharField(max_length=220,verbose_name='主图')
    imgOne = models.CharField(max_length=220)
    imgTwo = models.CharField(max_length=220)
    imgThree = models.CharField(max_length=220)
    detailImg = models.CharField(max_length=220,verbose_name='详情图')
    canuseCoupon = models.CharField(max_length=50,default='',verbose_name='是否使用优惠券')
    color = models.CharField(max_length=100,default='')
    size = models.CharField(max_length=100,default='')
    storeNum = models.IntegerField(default=100,verbose_name='库存')
#促销优惠券
class Coupon(models.Model):
    require = models.IntegerField(default='')
    reduce = models.IntegerField(default= '')

# type7种状态：1、待支付，  2、已支付待收货,21未揽件，22已揽件， 3、已收货（31满七天交易已完成，32未满七天可退款） 4、退货（41退货中；42退货失败；43退货成功）
#waitpay,waitget,canback,end
#周边产品下单信息
class AroundOrder(models.Model):
    orderNum = models.CharField(max_length=100,unique=True,verbose_name='订单号')
    userid = models.CharField(max_length=100)
    orderTime = models.CharField(max_length=50,verbose_name='下单时间')
    payTime = models.CharField(max_length=50,verbose_name='支付时间')
    receiveTime = models.CharField(max_length=50,verbose_name='收货时间')
    orderTruePay = models.DecimalField(decimal_places=2,max_digits=7)
    locationId = models.IntegerField(default=0)
    postageFee = models.IntegerField(default=0)
    couponReduce = models.IntegerField(default=0,verbose_name='优惠金额')
    waybillId = models.CharField(max_length=50,verbose_name='运单ID')
    logisticsInfo = models.CharField(max_length=100,verbose_name='物流信息')
    message = models.CharField(max_length=100,verbose_name='留言')
    ispay = models.BooleanField(default=0)
    isDelete = models.BooleanField(default=0)
    orderStatus = models.IntegerField(default=0,verbose_name='订单状态')

#周边下单 商品详情
class AroundOrderDetail(models.Model):
    goodId = models.IntegerField()
    goodName = models.CharField(max_length=50)
    goodPrice = models.DecimalField(decimal_places=2,max_digits=7)
    goodNum = models.IntegerField(default=0,verbose_name='下单商品数量')
    goodImg = models.CharField(max_length=225)
    orrderForeignkey = models.ForeignKey(AroundOrder,on_delete=models.CASCADE,default=1)
#收货人信息
class LocationNote(models.Model):
    consignee = models.CharField(max_length=50,verbose_name='收货人')
    mobile = models.CharField(max_length=50)
    isDefault = models.BooleanField(default=0)
    address = models.CharField(max_length=100,verbose_name='地址')
    addressDetail = models.CharField(max_length=200,verbose_name='详细地址')
    userid = models.CharField(max_length=100)

#关联表(购物车)
class Association(models.Model):
    userid = models.CharField(max_length=100)
    goodid = models.CharField(max_length=100)
    num = models.IntegerField(default=0)
    isdelete = models.BooleanField(default=0)
    class Meta:
        unique_together = ('userid','goodid')

