# -*- coding: UTF-8 -*-
from django.db import models

# Create your models here.
#发布帖子
class Posts(models.Model):
    userid = models.CharField(max_length=50)
    title = models.CharField(max_length=50)
    onlyTitle = models.CharField(max_length=100,default=0,db_index=True)
    time = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=1024)
    imgOne = models.CharField(max_length=200,default=0)
    imgTwo = models.CharField(max_length=200,default=0)
    imgThree = models.CharField(max_length=200,default=0)
    top = models.BooleanField(default=0)
    likeNums = models.IntegerField(default=0)
    commentNums = models.IntegerField(default=0)
    isSwipper = models.BooleanField(default=0)
    isDelete = models.BooleanField(default=0)

#主评论表
class MainComment(models.Model):
    postId = models.CharField(max_length=50) #帖子ID
    mainOpenid = models.CharField(max_length=50) #发布主评论人的openid
    mainContent = models.CharField(max_length=50)
    mainLikeNums = models.IntegerField(default=0)
    mainToOpenid = models.CharField(max_length=50) #发布帖子人的openid
    mainIsRead = models.BooleanField(default=0)
    mainTime = models.DateTimeField(auto_now_add=True) #评论时间
    mainEndtime = models.DateTimeField(auto_now_add=True)#最后一次评论时间

#副评论表
class SideComment(models.Model):
    postId = models.CharField(max_length=50) #帖子ID
    mainCommentId = models.CharField(max_length=50) #主评论ID
    mainOpenid = models.CharField(max_length=50)#主评论人openID
    sideOpenid = models.CharField(max_length=50) #副评论人openID
    sideContent = models.CharField(max_length=50)
    sideIsRead = models.BooleanField(default=0)
    sideTime = models.DateTimeField(auto_now_add=True)

#点赞帖子表
class LikePost(models.Model):
    postId = models.CharField(max_length=50)
    makeLikeOpenid = models.CharField(max_length=50) #点赞人openid
    getLikeOpenid = models.CharField(max_length=50)#被点赞人openid
    isRead = models.BooleanField(default=0)
    isDelete = models.BooleanField(default=0)

#点赞主评论表
class LikeMainComment(models.Model):
    postId = models.CharField(max_length=50)
    makeLikeOpenid = models.CharField(max_length=50)  # 点赞人openid
    getLikeOpenid = models.CharField(max_length=50)  # 被点赞人openid
    isRead = models.BooleanField(default=0)
    isDelete = models.BooleanField(default=0)

#收藏帖子表
class CollectPost(models.Model):
    postId = models.CharField(max_length=50)
    collector = models.CharField(max_length=50)

#举报帖子
class Report(models.Model):
    postId = models.CharField(max_length=50)
    content = models.CharField(max_length=50)