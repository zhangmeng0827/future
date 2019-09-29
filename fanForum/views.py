# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import *
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from customer.models import *
from itertools import chain
# Create your views here.
def test(request):
    return HttpResponse('just do it!!!')

#将对象数据转换为字典
def toDict(obj):
    setDict = {}
    for data in obj._meta.fields():
        try:
            name = data.name
            #获取对象属性值
            value = getattr(obj,name)
            setDict[name] = value
        except:
            continue #报错则跳过本次循环
    return setDict

#存储发布的帖子
def writePosts(request):
    userid = request.POST.get('userid')
    title = request.POST.get('title')
    content = request.POST.get('content')
    onlyTitle = userid + title
    imgOne = request.POST.get('imgOne')
    imgTwo = request.POST.get('imgTwo')
    imgThree = request.POST.get('imgThree')
    #判断是否发同标题的帖子
    isRepeat = Posts.objects.filter(onlyTitle=onlyTitle,isDelete=0)
    if isRepeat.exists():
        data = {'status':0,'msg':'亲，您发的帖子重复了哦!'}
        return JsonResponse(data)
    else:
        #存入数据库，新建帖子对象
        post = Posts()
        post.userid = userid
        post.title = title
        post.content = content
        post.onlyTitle = onlyTitle
        post.imgOne = imgOne
        post.imgTwo = imgTwo
        post.imgThree = imgThree
        post.save()
        user = User.objects.filter(userid=userid)
        user.postNum +=1
        user.experience += 10
        user.save()
    return JsonResponse({'status':1})

#粉丝论坛帖子展示
def showIndexPosts(request):
    #筛选出id小于或者等于100的帖子
    indexPosts = Posts.objects.filter(pk_lt=100)
    sendData = []
    for post in indexPosts:
        #创建帖子字典
        postObj = {}
        #将帖子数据转化为字典
        dictPosts = toDict(post)
        #获取发帖内容
        dictPosts['postId'] = dictPosts.pop('id')
        dictPosts['onlyTitle'] = dictPosts.pop('onlyTitle')
        postObj['postData'] = dictPosts

        #获取发帖用户信息
        openId = post.userid[0:-3]
        user = User.objects.get(pk=openId)
        userObj = {}
        userObj['userid'] = user.userid
        userObj['Nickname'] = user.Nickname
        userObj['avatarurl'] = user.avatarurl
        userObj['gender'] = user.gender

        postObj['userInfo'] = userObj

        sendData.append(postObj)

    return JsonResponse({'status':1,'indexData':sendData})

#粉丝论坛精选帖子展示（点赞数超过200）
def showChoicePosts(request):
    choicePosts = Posts.objects.filter(likeNums__gte=200)
    sendData = []
    for post in choicePosts:
        # 创建帖子字典
        postObj = {}
        # 将帖子数据转化为字典
        dictPosts = toDict(post)
        # 获取发帖内容
        dictPosts['postId'] = dictPosts.pop('id')
        dictPosts['onlyTitle'] = dictPosts.pop('onlyTitle')
        postObj['postData'] = dictPosts

        # 获取发帖用户信息
        openId = post.userid[0:-3]
        user = User.objects.get(pk=openId)
        userObj = {}
        userObj['userid'] = user.userid
        userObj['Nickname'] = user.Nickname
        userObj['avatarurl'] = user.avatarurl
        userObj['gender'] = user.gender

        postObj['userInfo'] = userObj

        sendData.append(postObj)

    return JsonResponse({'status': 1, 'indexData': sendData})

#社区搜索帖子
def showSearchPosts(request):
    keyWords = request.POST.get('keyWords')
    searchPosts = Posts.objects.filter(title__contains=keyWords).order_by('-commentNums')
    sendData = []
    for post in searchPosts:
        # 创建帖子字典
        postObj = {}
        # 将帖子数据转化为字典
        dictPosts = toDict(post)
        # 获取发帖内容
        dictPosts['postId'] = dictPosts.pop('id')
        dictPosts['onlyTitle'] = dictPosts.pop('onlyTitle')
        dictPosts['time'] = str(dictPosts['time'])[0:19].replace('T',' ')
        postObj['postData'] = dictPosts

        # 获取发帖用户信息
        openId = post.userid[0:-3]
        user = User.objects.filter(pk=openId)
        userObj = {}
        userObj['userid'] = user.userid
        userObj['Nickname'] = user.Nickname
        userObj['avatarurl'] = user.avatarurl
        userObj['gender'] = user.gender

        postObj['userInfo'] = userObj

        sendData.append(postObj)

    return JsonResponse({'status': 1, 'indexData': sendData})

#粉丝论坛帖子展示（置顶贴+按发帖时间(5个贴)+按评论数(降序))
#设置缓存时间5秒
@cache_page(5)
def showPosts(request):
    page = request.POST.get('page')
    page = int(page)
    #检查缓存中是否存在所需要的帖子
    sumPosts = cache.get('sumPosts')
    if sumPosts == None:
        topPosts = Posts.objects.filter(top=1,isDelete=0)
        allPosts = Posts.objects.filter(top=0,isDelete=0).orderby("-time")
        fivePosts = allPosts[:5]
        commentPosts = sorted(allPosts[5:],key=lambda x:x.comment_num,reverse=True)
        sumPosts = list(chain(topPosts,fivePosts,commentPosts))
        #存入redis缓存,过期时间20秒
        cache.set("sumPosts",sumPosts,20)
    toShowPosts = sumPosts[(page-1)*25:page*25]
    listdata = []
    for toShowPost in toShowPosts:
        postObj = {}
        dictPosts = toDict(toShowPost)
        dictPosts["time"] = str(dictPosts['time'])[0:19].replace('T',' ')
        postObj['postData'] = dictPosts

        userObj = {}
        openid = dictPosts["userid"][0:-3]
        user= User.objects.filter(pk=openid)
        userObj['userid'] = user.userid
        userObj['Nickname'] = user.Nickname
        userObj['avatarurl'] = user.avatarurl
        userObj['gender'] = user.gender
        postObj['userInfo'] = userObj

        listdata.append(postObj)
    return JsonResponse({'status':1,'data':listdata})

#查看关注人的帖子
def focusPosts(request):
    userid = request.POST.get('userid')
    page = int(request.POST.get('page'))
    concerns = Concern.objects.filter(userid=userid)
    sendData = []
    for concern in concerns:
        #关注的人的userid
        concern_userid = concern.concern_userid
        #关注的人
        concern = concern.concern
        #获取关注的人的用户信息
        concernUserData = {}
        concernUserData['userid'] = concern.userid
        concernUserData['Nickname'] = concern.Nickname
        concernUserData['avatarurl'] = concern.avatarurl
        concernUserData['gender'] = concern.gender
        #获取关注的人的帖子信息
        posts = Posts.objects.filter(userid=concern_userid)
        for post in posts:
            postObj = {}
            dictPost = toDict(post)
            dictPost['time'] = str(dictPost['time'])[:19].replace('T',' ')
            postObj['postData'] = dictPost
            postObj['concernUserData'] = concernUserData
            sendData.append(postObj)
    #页数小于2时，一页展示100条
    if page<2:
        sendData = sorted(sendData,key=lambda x:x['postData']['time'],reverse=True)[0:100]
    else:
        sendData = sorted(sendData,key=lambda x:x['postData']['time'],reverse=True)[(page-1)*100:page*100]
    return JsonResponse({'status':1,'data':sendData})

#展示轮播图帖子
#缓存1h
@cache_page(60*60,cache='longtime')
def showSwipper(request):
    swipperPosts = Posts.objects.filter(isSwipper=1,isDelete=0)
    sendData = []
    for swipperPost in swipperPosts:
        postObj = {}
        dictPosts = toDict(swipperPost)
        dictPosts['postId'] = dictPosts.pop('id')
        dictPosts.pop('onlyTitle')
        postObj['postData'] = dictPosts

        userInfo = {}
        openid = swipperPost.userid[0:-3]
        user = User.objects.get(openid=openid)
        userInfo['userid'] = user.userid
        userInfo['Nickname'] = user.Nickname
        userInfo['avatarurl'] = user.avatarurl
        userInfo['gender'] = user.gender
        postObj['userInfo'] = userInfo

        sendData.append(postObj)
    return JsonResponse({'status':1,'data':sendData})

#主评论展示
def showMainComment(request):
        postId = request.POST.get('postId')
        mainOpenid = request.POST.get('mainOpenid')
        mainToOpenid = request.POST.get('mainToOpenid')
        mainContent = request.POST.get('mainContent')

        if mainOpenid == mainToOpenid:
            comment = MainComment.objects.get_or_create(postId=postId,mainContent=mainContent,mainIsRead=1,mainOpenid=mainOpenid
                                                        ,mainToOpenid=mainToOpenid)
        else:
            comment = MainComment.objects.get_or_create(postId=postId,mainContent=mainContent,mainOpenid=mainOpenid
                                                        ,mainToOpenid=mainToOpenid)

        if False in comment:
            return JsonResponse({'status':1,'data':'不可评论相同内容'})
        #帖子评论数加一
        else:
            post = Posts.objects.get(id=postId)
            post.commentNums+=1
            post.save()
            return JsonResponse({'status':1,'data':'评论成功'})

#副评论展示
def showSideComment(request):
    postId = request.POST.get('postId')
    mainCommentId = request.POST.get('mainCommentId')
    mainOpenId = request.POST.get('mainOpenid')
    sideOpenId = request.POST.get('sideOpenid')
    sideContent = request.POST.get('sideContent')

    if mainOpenId == sideOpenId:
        comment = SideComment.objects.get_or_create(postId=postId,mainCommentId=mainCommentId,mainOpenId=mainOpenId,
                                                    sideOpenId=sideOpenId,sideIsRead=1,sideContent=sideContent)
    else:
        comment = SideComment.objects.get_or_create(postId=postId,mainCommentId=mainCommentId,mainOpenId=mainOpenId,
                                                    sideOpenId=sideOpenId,sideContent=sideContent)
    if False in comment:
        return JsonResponse({'status':1,'data':'不可评论相同内容'})

    else:
        post = Posts.objects.get(id=postId)
        post.commentNums+=1
        post.save()
    #更新主评论时间
        mainComment = MainComment.objects.get(mainCommentId=mainCommentId)
        comment[0].mainTime = mainComment.mainEndtime
        mainComment.save()
        return JsonResponse({'status':1,'data':'评论成功'})




