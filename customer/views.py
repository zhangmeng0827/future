# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.db.models import Q
from .models import Student
from customer.logic_getdata_fromweixn import *
from customer.WXBizDataCrypt import *
from customer.models import *

import hashlib
import time
import random
# Create your views here.

def hello(request):
    return HttpResponse('just do it!!! ')

def insertdata(request):
    stu = Student()
    stu.name = 'kobe'
    stu.sex = '女'
    stu.old = 18
    stu.save()
    return JsonResponse({'statu':1})
    # return HttpResponse('insertdata ok')
def select_data(request):
    stu = Student.objects.filter(old=22)
    print(list(stu))
    return HttpResponse('ok')

def handle(request):
    print(request.path)
    try:
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        echostr = request.GET.get('echostr')
        token = 'liulian'

        print(signature)
        print (timestamp)
        print (nonce)
        print (echostr)

        list = [token,timestamp,nonce]
        list.sort()
        list2 = ''.join(list)

        sha1= hashlib.sha1()
        sha1.update(list2.encode('utf-8'))
        hashcode = sha1.hexdigest()

        if signature == hashcode:
            return HttpResponse(echostr)
        else:
            return HttpResponse(False)
    except Exception as e:
        return  HttpResponse(e)

def get_echosor(request):
    if request.method == 'GET':
        echostr = request.GET.get('echostr')
        return HttpResponse(echostr)

#生成加密十六进制的token
def get_token():
    token = str(time.time())+ str(random.random())
    #创建MD5加密算法对象
    md5 = hashlib.sha1()
    #进行加密
    md5.update(token.encode('utf-8'))
    #转为16进制
    token = md5.hexdigest()
    # return token
    return token

#获取新用户信息
def get_userinfo(request):
    #获取加密数据
    encryptdata = request.POST.get('encryptdata')
    #获取解密向量
    iv = request.POST.get('iv')
    #获取临时登陆凭证
    code = request.POST.get('code')
    #通过微信接口获取unionid、openid、sessionkey、errorde、errmsg,字典
    data = get_unionid(code)
    #查看是否有错误信息
    if data['errorde']:
        errmsg = data.get('errmsg')
        err_dict = dict(status=0,errmsg=errmsg,errorde=data.get('errorde'))
        return JsonResponse(err_dict)
    #判断用户是否为初次登录
    else:
        openid = data['openid']
        user = User.objects.filter(pk=openid)
        if not user.exixts():
            sessionkey = data['sessionkey']
            userdata = getuserdata(sessionkey,iv,encryptdata)
            #将用户数据存入数据库
            Nickname = userdata.get('Nickname')
            avatarurl = userdata.get('avatarurl')
            language = userdata.get('language')
            gender = userdata.get('gender')
            country = userdata.get('country')
            province = userdata.get('province')
            city = userdata.get('city')
            token = get_token()
            unionid = userdata.get('unionid')
            userid = str(openid) + random.randint(333,667)

            #创将新用户对象
            new_user = User()
            new_user.Nickname = Nickname
            new_user.avatarurl = avatarurl
            new_user.language = language
            new_user.gender = gender
            new_user.country = country
            new_user.province = province
            new_user.city = city
            new_user.token = token
            new_user.unionid = unionid
            new_user.token = token
            new_user.userid = userid
            new_user.save()

            #登录送优惠券
            pass
        #非初次登录
        else:
            user = user[0]
            userid = user.userid
            token = user.token
            Nickname = user.Nickname
            avatarurl = user.avatarurl
            gender = user.gender
            language = user.language
        #获取用关注数、粉丝数、帖子数
        post_num = user.post_num
        concern_num = user.concern_num
        fans_num = user.fans_num
        old_data = {
            'status':1,
            'old_user_data':{
                'userid': userid,
                'token':token,
                'Nickname':Nickname,
                'avatarurl':avatarurl,
                'gender':gender,
                'language':language,
                'post_num':post_num,
                'fans_num':fans_num,
                'concern_num':concern_num,
            }

        }
        return JsonResponse(old_data)


#获取老用户详情
def get_old_userdata(request):
    token = request.POST.get('token')
    user = User.objects.get(token=token)
    userid = user.userid
    token = user.token
    Nickname = user.Nickname
    avatarurl = user.avatarurl
    gender = user.gender
    language = user.language
    old_userdata= {
        'status':1,
        'old_userdata':{
            'userid':userid,
            'token':token,
            'Nickname':Nickname,
            'avatarurl':avatarurl,
            'gender':gender,
            'language':language,
        }


    }
    return JsonResponse(old_userdata)

#浏览用户详情
pass
#确认消息是否已读
def isread(request):
    userid = request.POST.get('userid')
    user = User.objects.filter(userid=userid)
    pass
#关注
def concern(request):
    #关注者的userid
    userid = request.POST.get('userid')
    #被关注者的userid
    concern_userid = request.POST.get('concern_userid')

    concern = User.objects.filter(userid=userid)[0]
    concern.concern_num +=1
    concern.save()

    #被关注者
    concern_user = User.objects.filter(userid=concern_userid)[0]
    concern_user.fans_num +=1
    concern_user.save()

    #存入数据库
    concern_people = Concern()
    concern_people.userid = userid
    concern_people.concern_userid = concern_userid
    concern_people.concern = concern_user
    concern_people.save()

    fans_people = Fans()
    fans_people.userid = concern_userid
    fans_people.fans_userid = userid
    fans_people.fans = concern
    fans_people.save()
    return JsonResponse({'status':1})
#取消关注
def cancel_concern(request):
    userid = request.POST.get('userid')
    concern_userid = request.POST.get('concern_userid')
    user = User.objects.filter(userid=userid)[0]
    user.concern_num -=1
    user.save()
    concern_user = User.objects.filter(userid=concern_userid)[0]
    concern_user.fans_num -=1
    concern_user.save()

    concern = User.objects.filter(Q(userid=userid))&(Q(concern=concern_userid))
    concern.delete()

    fans = User.objects.filter(Q(userid=concern_userid))&(Q(fans = user))
    fans.delete()
    return JsonResponse({'status':1})
#我的关注
def my_concern(request):
    userid = request.POST.get('userid')
    concerns = Concern.objects.filter(userid=userid)
    concern_data = []
    if concerns.exists():
        for concern in concerns:
            user = concern.concern
            user_data = {}
            user_data['Nickname'] = user.Nickname
            user_data['userid'] = user.userid
            user_data['gender'] = user.gender
            user_data['avatarurl'] = user.avatarurl
            user_data['hidden'] = False
            concern_data.append(user_data)
    return JsonResponse({'data':concern_data})
#我的粉丝
def my_fans(request):
    userid = request.POST.get('userid')
    fans = Fans.objects.filter(userid=userid)
    fans_data = []
    if fans.exists():
        for fan in fans:
            user = fan.fans
            user_data = {}
            user_data['Nickname'] = user.Nickname
            user_data['userid'] = user.userid
            user_data['gender'] = user.gender
            user_data['avatarurl'] = user.avatarurl
            user_data['hidden'] = False
            fans_data.append(user_data)
    return JsonResponse({'data':fans_data})



