# -*- coding: UTF-8 -*-
from django.db import models

# Create your models here.
class Student(models.Model):
    name = models.CharField(max_length=10)
    sex = models.CharField(max_length=10)
    old = models.IntegerField()
    isdelete = models.BooleanField(default=False)

class User(models.Model):
    userid = models.CharField(max_length=50)
    openid = models.CharField(max_length=50,primary_key=True) #primary_key=True代表openid字段为主键
    Nickname = models.CharField(max_length=50)
    gender = models.IntegerField(default=1)
    language = models.CharField(max_length=50)
    avatarurl = models.CharField(max_length=100)
    country = models.CharField(max_length=50)
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    token = models.CharField(max_length=100,unique=True)
    unionid = models.CharField(max_length=50)
    experience = models.IntegerField(default=0)
    postNum = models.IntegerField(default=0)  # 发帖数
    concernNum = models.IntegerField(default=0)
    fansNum = models.IntegerField(default=0)

class Concern(models.Model):
    userid = models.CharField(max_length=50)
    concern_userid = models.CharField(max_length=50)
    concern = models.ForeignKey(User,on_delete=models.CASCADE)  #一对多关系，字段定义在多的一端

class Fans(models.Model):
    userid = models.CharField(max_length=50)
    fans_userid = models.CharField(max_length=50)
    fans = models.ForeignKey(User,on_delete=models.CASCADE)  #一对多关系，字段定义在多的一端
