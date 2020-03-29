#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "qiu"
__date__ = "2019-07-03 16:47"
import datetime
import hashlib
import jwt
import json
import re
import time
from tools.logging_check import logging_check
from tools.configs import make_token, CODE_TOKEN_KEY
from django.contrib.auth.hashers import make_password, check_password
from .tasks import send_sms_code
from django.http import JsonResponse, HttpResponse  # 用于返回json数据
from django.shortcuts import render, get_object_or_404  # 用于页面后台渲染，用于使用报错模式获取对象（如果找不到该对象，则报404错误）
from django.views.generic import View  # 使用Django自带的视图处理不同类型的请求
from django.views.decorators.csrf import csrf_exempt  # 用于标识一个视图可以被跨域访问
from django.db.models import Q  # Q查询——对对象的复杂查询

from .models import Blog, Category, Conment, Tagprofile, User


# 使用继承自View的视图类，可以直接定义get或post的方法
class Index(View):
    """首页显示"""
    # 调用view的as_view方法触发
    # 浏览器发送来一个get请求，get存在于http_method_names列表中，
    # 所以是个合法的http方法，此时通过getattr获取到自定义Index类视图中的get方法，
    # 并将get方法的引用传给handler（所以我们需要在自定义类视图中定义get方法，
    # 否则dispatch找不到get方法，比如开头的例子中，我们需要在Index类中定义get方法）
    # ，最后执行get方法，并返回执行结果
    def get(self, request): #执行
        # 以下部分可以定义为全局变量
        tag_list = Tagprofile.objects.all()  # 标签云
        category_list = Category.objects.all()  # 分类
        comment_list = Conment.objects.all().order_by('-add_time')[:20]  # 最新评论

        # 首页最新文章列表，按照编辑时间进行排序，取前5篇进行展示
        article_list = Blog.objects.all().order_by('-edit_time')[:5]
        # 首页最热文章列表，按照评论数量进行排序，取前5篇进行展示
        article_rank = Blog.objects.all().order_by('-conment_nums')[:5]

        # 使用render()，在后端对页面进行渲染
        return render(request, 'index.html', {
            'article_list': article_list,
            'article_rank': article_rank,
            'category_list': category_list,
            'tag_list': tag_list,
            'comment_list': comment_list,
        })


class About(View):
    """
    关于
    自定义页面，可作为个人简历，直接编辑about.html页面
    """

    def get(self, request):
        # 以下部分可以定义为全局变量
        tag_list = Tagprofile.objects.all()  # 标签云
        category_list = Category.objects.all()  # 分类
        article_rank = Blog.objects.all().order_by('-conment_nums')[:10]  # 热门博客
        comment_list = Conment.objects.all().order_by('-add_time')[:20]  # 最新评论

        return render(request, 'about.html', {
            'article_rank': article_rank,
            'category_list': category_list,
            'tag_list': tag_list,
            'comment_list': comment_list,
        })


class Articles(View):
    """博客文章列表页面"""

    def get(self, request, pk):
        # 以下部分可以定义为全局变量
        tag_list = Tagprofile.objects.all()  # 标签云
        category_list = Category.objects.all()  # 分类
        article_rank = Blog.objects.all().order_by('-conment_nums')[:10]  # 热门博客
        comment_list = Conment.objects.all().order_by('-add_time')[:20]  # 最新评论

        # 获取指定分类的文件
        if pk:
            category_obj = get_object_or_404(Category, id=pk)
            category = category_obj.name
            article_list = Blog.objects.filter(category_id=pk)
        else:  # pk=0时，获取全部列表
            article_list = Blog.objects.all()
            category = ''
        count = article_list.count()

        return render(request, 'articles.html', {
            'article_list': article_list,
            'category': category,
            'count': count,
            'category_list': category_list,
            'tag_list': tag_list,
            'article_rank': article_rank,
            'comment_list': comment_list,

        })


class Archive(View):
    """归档，以时间线展示博客文章历程"""

    def get(self, request):
        # 以下部分可以定义为全局变量
        tag_list = Tagprofile.objects.all()  # 标签云
        category_list = Category.objects.all()  # 分类
        article_rank = Blog.objects.all().order_by('-conment_nums')[:10]  # 热门博客
        comment_list = Conment.objects.all().order_by('-add_time')[:20]  # 最新评论

        # 对编辑时间进行排序
        article_list = Blog.objects.all().order_by('-edit_time')

        return render(request, 'archive.html', {
            'article_list': article_list,
            'category_list': category_list,
            'tag_list': tag_list,
            'article_rank': article_rank,
            'comment_list': comment_list,
        })


class Link(View):
    """链接，可以放入多个页面链接，直接编辑link.html页面"""

    def get(self, request):
        # 以下部分可以定义为全局变量
        tag_list = Tagprofile.objects.all()  # 标签云
        category_list = Category.objects.all()  # 分类
        article_rank = Blog.objects.all().order_by('-conment_nums')[:10]  # 热门博客
        comment_list = Conment.objects.all().order_by('-add_time')[:20]  # 最新评论

        return render(request, 'link.html', {
            'category_list': category_list,
            'tag_list': tag_list,
            'article_rank': article_rank,
            'comment_list': comment_list,
        })


class Message(View):
    """留言"""

    def get(self, request):
        # 以下部分可以定义为全局变量
        tag_list = Tagprofile.objects.all()  # 标签云
        category_list = Category.objects.all()  # 分类
        article_rank = Blog.objects.all().order_by('-conment_nums')[:10]  # 热门博客
        comment_list = Conment.objects.all().order_by('-add_time')[:20]  # 最新评论

        return render(request, 'message_board.html', {
            'category_list': category_list,
            'tag_list': tag_list,
            'article_rank': article_rank,
            'comment_list': comment_list,
        })


class Search(View):
    """搜索"""

    def get(self, request): #等价于 if request.method == "GET";
        # 以下部分可以定义为全局变量
        tag_list = Tagprofile.objects.all()  # 标签云
        category_list = Category.objects.all()  # 分类
        article_rank = Blog.objects.all().order_by('-conment_nums')[:10]  # 热门博客
        comment_list = Conment.objects.all().order_by('-add_time')[:20]  # 最新评论

        key = request.GET.get('key', '')
        if key:
            # 使用Q查询，对标题、博文内容进行全局搜索
            article_list = Blog.objects.filter(Q(title__icontains=key) | Q(content__icontains=key))

        else:
            article_list = ''
        count = article_list.count()
        return render(request, 'search.html', {
            'category_list': category_list,
            'tag_list': tag_list,
            'article_rank': article_rank,
            'comment_list': comment_list,
            'article_list': article_list,
            'count': count,
            'key': key,
        })


@csrf_exempt
def GetComment(request):
    """
    接收畅言的评论回推， post方式回推
    """
    try:
        arg = request.POST
        data = arg.get('data')
        data = json.loads(data)
        title = data.get('title')
        url = data.get('url')
        source_id = data.get('sourceid')
        if source_id not in ['message']:
            article = Blog.objects.get(id=source_id)
            article.commenced()
        comments = data.get('comments')[0]
        content = comments.get('content')
        user = comments.get('user').get('nickname')
        Conment(title=title, source_id=source_id, user=user, url=url, conment=content).save()
        return JsonResponse({"status": "ok"})
    except BaseException as e:
        return JsonResponse({"status": "failed"})


class Detail(View):
    """博客详情页"""

    def get(self, request, pk):
        # 以下部分可以定义为全局变量
        tag_list = Tagprofile.objects.all()  # 标签云
        category_list = Category.objects.all()  # 分类
        article_rank = Blog.objects.all().order_by('-conment_nums')[:10]  # 热门博客
        comment_list = Conment.objects.all().order_by('-add_time')[:20]  # 最新评论

        article = get_object_or_404(Blog, id=pk)

        # 增加阅读数
        article.viewed()

        return render(request, 'detail.html', {
            'article': article,
            'source_id': article.id,
            'tag_list': tag_list,
            'category_list': category_list,
            'article_rank': article_rank,
            'comment_list': comment_list,
        })


class Tagcloud(View):
    """
    标签云
    当点击标签时，显示有此标签的所有文章
    """

    def get(self, request, id): #if request.method == "GET"
        # 以下部分可以定义为全局变量
        tag_list = Tagprofile.objects.all()  # 标签云
        category_list = Category.objects.all()  # 分类
        article_rank = Blog.objects.all().order_by('-conment_nums')[:10]  # 热门博客
        comment_list = Conment.objects.all().order_by('-add_time')[:20]  # 最新评论

        tag = get_object_or_404(Tagprofile, id=id).tag_name
        article_list = Blog.objects.filter(tag__tag_name=tag)
        count = article_list.count()
        return render(request, 'tag.html', {
            'tag': tag,
            'article_list': article_list,
            'category_list': category_list,
            'tag_list': tag_list,
            'article_rank': article_rank,
            'comment_list': comment_list,
            'count': count,
        })

class Login(View):
    """登录界面"""
    def get(self,request):
        return render(request,"login.html")
    
    @csrf_exempt
    def post(self,request):
        json_str = request.body
        json_obj = json.loads(json_str)
        login_mode = json_obj.get("login_mode")
        user_t = None
        print("json_obj:", json_obj)
        if login_mode == "sms_login": #短信验证码登录
            phone = json_obj.get("phone")
            user = User.objects.get(phone=phone)
            if not user:
                result = {"code": 10103, "error": "The user not existed!"}
                response = JsonResponse(result)
                #response["Access-Control-Allow-Origin"] = "*"
                #response["Access-Control-Allow-Methods"] = "*"
                #response["Cache-Control"]= "no-cache"
                return response
            ver_code = json_obj.get("ver_code")
            if not ver_code:
                result = {"code":10108,"error":"Vertify code cannot be empty!!"}
                return JsonResponse(result)
            code_token = json_obj.get("code_token")
            if not code_token:
                result = {"code": 10102, "error": "Vertifying failed!"} 
                response = JsonResponse(result)
                #response["Access-Control-Allow-Origin"] = "*"
                #response["Access-Control-Allow-Methods"] = "*"
                #response["Cache-Control"]= "no-cache"
                return response
            try:
                json_obj = jwt.decode(code_token, key=CODE_TOKEN_KEY, algorithms="HS256")
            except Exception as e:
                result = {"code": 10102, "error": "Vertifying failed!"} 
                response = JsonResponse(result)
                #response["Access-Control-Allow-Origin"] = "*"
                #response["Access-Control-Allow-Methods"] = "*"
                #response["Cache-Control"]= "no-cache"
                return response
            code_expired_time = json_obj.get("exp")
            if not code_expired_time:
                result = {"code": 10108, "error": "Vertifying failed!!"} 
                response = JsonResponse(result)
                #response["Access-Control-Allow-Origin"] = "*"
                #response["Access-Control-Allow-Methods"] = "*"
                #response["Cache-Control"]= "no-cache"
                return response
            if time.time() > code_expired_time:
                result = {"code": 10102, "error": "Vertifying is overtime!!"} 
                response = JsonResponse(result)
                #response["Access-Control-Allow-Origin"] = "*"
                #response["Access-Control-Allow-Methods"] = "*"
                #response["Cache-Control"]= "no-cache"
                return response
            if ver_code != json_obj["code"]:
                result = {"code": 10109, "error": "Vertifying failed!"}
                response = JsonResponse(result)
                #response["Access-Control-Allow-Origin"] = "*"
                #response["Access-Control-Allow-Methods"] = "*"
                #response["Cache-Control"]= "no-cache"
                return response
            user_t = user

        elif login_mode == "uname_login":
            username = json_obj.get("username","")
            password = json_obj.get("password","")
            if not username:
                result = {"code": 20102, "error": "The username cannot empty!"}
                response = JsonResponse(result)
                #response["Access-Control-Allow-Origin"] = "*"
                #response["Access-Control-Allow-Methods"] = "*"
                #response["Cache-Control"]= "no-cache"
                return response
            if not password:
                result = {"code":20102,"error":"The password cannot empty"}
                response = JsonResponse(result)
                #response["Access-Control-Allow-Origin"] = "*"
                #response["Access-Control-Allow-Methods"] = "*"
                #response["Cache-Control"]= "no-cache"
                return response
            print("password:", password)
            # 找用户
            user = User.objects.get(username=username)
            if not user:
                result = {"code": 20102, "error": "The username or password is error!!"}
                response = JsonResponse(result)
                #response["Access-Control-Allow-Origin"] = "*"
                #response["Access-Control-Allow-Methods"] = "*"
                #response["Cache-Control"]= "no-cache"
                return response
            print("user.username:",user.username)

            pbk_pswd = user.password
            print("pbk_pswd:",pbk_pswd)

            pwd_bool = check_password(password,pbk_pswd)  # 返回的是一个bool类型的值，验证密码正确与否
            print("pwd_bool:",pwd_bool)
            if not pwd_bool:
                result = {"code": 20103, "error": "The username or password is error!!"}
                response = JsonResponse(result)
                #response["Access-Control-Allow-Origin"] = "*"
                #response["Access-Control-Allow-Methods"] = "*"
                #response["Cache-Control"]= "no-cache"
                return response
            user_t = user

        # 生成token
        now_d = datetime.datetime.now()
        user_t.login_time = now_d
        user_t.save()  # 数据保存更新
        token = make_token(user_t.username, 3600 * 24, now_d)
        result = {"code": 200, "username": user_t.username, "data": {"token": token.decode()}}

        response = JsonResponse(result)
        #response["Access-Control-Allow-Origin"] = "*"
        #response["Access-Control-Allow-Methods"] = "*"
        #response["Cache-Control"]= "no-cache"
        return response

class Register(View):
    """注册界面"""
    def get(self,request):
        return render(request,"register.html")
    @csrf_exempt
    def post(self,request):
        result = {"code":10104,"error":"对不起,暂时未开通注册功能,非常抱歉!!"}
        response = JsonResponse(result)
        #response["Access-Control-Allow-Origin"] = "*"
        #response["Access-Control-Allow-Methods"] = "*"
        #response["Cache-Control"]= "no-cache"
        return response

class SmsLogin(View):
    """短信登录界面"""
    def get(self,request):
        return render(request,"sms_login.html")
    @csrf_exempt
    def post(self,request):
        result = {"code":10104,"error":"对不起,暂时未开通短信登录功能,非常抱歉!!"}
        response = JsonResponse(result)
        #response["Access-Control-Allow-Origin"] = "*"
        #response["Access-Control-Allow-Methods"] = "*"
        #response["Cache-Control"]= "no-cache"
        return response

@csrf_exempt
@logging_check("POST")
def check_status(request):
    if request.method != "POST":
        result = {"code":10102,"error":"please use post!"}
        response = JsonResponse(result)
        #response["Access-Control-Allow-Origin"] = "*"
        #response["Access-Control-Allow-Methods"] = "*"
        #response["Cache-Control"]= "no-cache"
        return response
    user = request.user
    json_str = request.body
    json_obj = json.loads(json_str) #字符串转为字典(json对象)
    username = json_obj.get("username","")
    print("username:",username)
    print("user.username:",user.username)
    if username != user.username:
        result = {"code":10102,"error":"username is error!!"}
        response = JsonResponse(result)
        #response["Access-Control-Allow-Origin"] = "*"
        #response["Access-Control-Allow-Methods"] = "*"
        #response["Cache-Control"]= "no-cache"
        return response
    result = {"code":200,"data":{"username":username}}
    response = JsonResponse(result)
    #response["Access-Control-Allow-Origin"] = "*"
    #response["Access-Control-Allow-Methods"] = "*"
    #response["Cache-Control"]= "no-cache"
    return response


def page_not_look(request):
    """全局403配置"""
    from django.shortcuts import render_to_response
    response = render_to_response('403.html', {})
    response.status_code = 403
    return response


def page_not_found(request):
    """全局404配置"""
    from django.shortcuts import render_to_response
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


def page_error(request):
    """全局500配置"""
    from django.shortcuts import render_to_response
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response

@csrf_exempt
def send_sms_codes(request):
    if request.method == "POST":
        json_str = request.body
        json_obj = json.loads(json_str)
        phone = json_obj.get("phone")
        if not phone: #注销1
            result = {"code": 10103, "error": "please enter a phone number"}
            response = JsonResponse(result)
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "*"
            response["Cache-Control"]= "no-cache"
            return response

        # 验证手机号是否正确
        phone_re = re.compile('^1[3-9]\d{9}$')
        res = re.search(phone_re, phone)

        if not res:  # 不正确
            result = {"code": 10104, "error": "The phone number is error!!"}
            response = JsonResponse(result)
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "*"
            response["Cache-Control"]= "no-cache"
            return response

        # delay 返回的是一个 AsyncResult 对象，里面存的就是一个异步的结果，
        # 当任务完成时result.ready() 为 true，然后用 result.get() 取结果即可。
        result = send_sms_code.delay(mobile=phone)  # 手机号,验证码
        print("apply_async的result:", result)
        count = 0  # 定时
        while not result.ready():
            time.sleep(0.1)
            count += 1
            if count == 10:
                break

        if result.ready():
            print("result.get的type", type(result.get()))
            print("result的结果", result.result)
            print("result的结果", result.get())
            response = JsonResponse(result.get())
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "*"
            response["Cache-Control"]= "no-cache"
            return response
        else:
            response = JsonResponse({"code": 10102, "error": "发送失败01"})
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "*"
            response["Cache-Control"]= "no-cache"
            return response

