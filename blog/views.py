# -*- coding: utf-8 -*-

import json
import random
import logging

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q, Count
from django.shortcuts import render, render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt

from blog.forms import CommentForm
from blog.models import *
from blog.utils import uploads, utils
from blog_project.settings import MAIL_USER
from blog_project.celery import send_email


@csrf_exempt
def page_not_found(request, exception):
    return render_to_response('404.html', {'description': utils.get_desc()})


@csrf_exempt
def page_error(request):
    return render_to_response('500.html', {'description': utils.get_desc()})


# @cache_page(1200)  # 视图缓存无法判断是否登录
def get_blogs(request):
    '''
    获取博客列表
    :param request:
    :return:
    '''
    Viewlog.objects.create(userId=request.session.get('uid', 0), ip=utils.getIP(request), blog_id=57).save()

    catagory = request.GET.get("catagory")
    tag = request.GET.get("tag")
    logger = logging.getLogger('app')

    try:
        if catagory:
            catagory = Catagory.objects.get(id=catagory)
            blogs = Blog.objects.all().order_by('-created'). \
                filter(isDraft=False, isDelete=False, catagory=catagory). \
                values('id', 'title', 'intro', 'read', 'created', 'catagory__name', comment_count=Count('comment'))
        elif tag:
            tag = Tag.objects.get(id=tag)
            blogs = Blog.objects.all().order_by('-created'). \
                filter(isDraft=False, isDelete=False, tags=tag). \
                values('id', 'title', 'intro', 'read', 'created', 'catagory__name', comment_count=Count('comment'))
        else:
            blogs = Blog.objects.all().order_by('-created'). \
                filter(isDraft=False, isDelete=False). \
                values('id', 'title', 'intro', 'read', 'created', 'catagory__name', comment_count=Count('comment'))
    except Exception:
        logger.info(
            'bloglist does not exist, catagory=%s, tag=%s, ip=%s' % (catagory, tag, utils.getIP(request)))
        # raise Http404
        return render_to_response('blog-sitemap.html', {'description': utils.get_desc()})

    # 从缓存中取 tags
    cache_dict = utils.get_tags_dict()
    for blog in blogs:
        if blog['id'] in cache_dict:
            blog['alltags'] = cache_dict[blog['id']]
        else:
            cache_dict = utils.get_tags_dict(True)
            blog['alltags'] = cache_dict[blog['id']]

    # 分页
    paginator = Paginator(blogs, 8)  # Show 8 contacts per page
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
        logger.info("paginator error, EmptyPage, ip=%s" % (utils.getIP(request)))

    if contacts.has_previous():
        if catagory:
            contacts.previous_url = '?catagory={}&page={}'.format(catagory.id, contacts.previous_page_number())
        elif tag:
            contacts.previous_url = '?tag={}&page={}'.format(tag.id, contacts.previous_page_number())
        else:
            contacts.previous_url = '?page={}'.format(contacts.previous_page_number())
    if contacts.has_next():
        if catagory:
            contacts.next_url = '?catagory={}&page={}'.format(catagory.id, contacts.next_page_number())
        elif tag:
            contacts.next_url = '?tag={}&page={}'.format(tag.id, contacts.next_page_number())
        else:
            contacts.next_url = '?page={}'.format(contacts.next_page_number())

    info = {'catagory': catagory, 'tag': tag, 'title': '张文迪的博客', 'description': utils.get_desc(), 'contacts': contacts}

    return render_to_response('blog-list.html', info)


def get_catagory(request):
    '''
    获取分类列表
    :param request:
    :return:
    '''
    Viewlog.objects.create(userId=request.session.get('uid', 0), ip=utils.getIP(request), blog_id=56).save()

    catagorys = Catagory.objects.filter(isDelete=False).values('id', 'name', 'remark')
    # if request.session.get('uid'):
    #     is_login = True
    # else:
    #     is_login = False

    info = {'catagorys': catagorys, 'title': '博客分类', 'description': utils.get_desc()}
    return render_to_response('blog-catagory.html', info)


def get_tag(request):
    '''
    获取标签列表
    :param request:
    :return:
    '''
    Viewlog.objects.create(userId=request.session.get('uid', 0), ip=utils.getIP(request), blog_id=55).save()

    tags = Tag.objects.filter(isDelete=False).values('id', 'name', 'remark')

    info = {'tags': tags, 'title': '博客标签', 'description': utils.get_desc()}
    return render_to_response('blog-tag.html', info)


def get_sitemap(request):
    '''
    获取标签列表
    :param request:
    :return:
    '''
    Viewlog.objects.create(userId=request.session.get('uid', 0), ip=utils.getIP(request), blog_id=54).save()

    tags = Tag.objects.filter(isDelete=False).values('id', 'name')
    catagorys = Catagory.objects.filter(isDelete=False).values('id', 'name')
    blogs = Blog.objects.all().order_by('-created').filter(isDraft=False, isDelete=False).values('id', 'title')

    info = {'tags': tags, 'catagorys': catagorys, 'blogs': blogs, 'title': '网站地图', 'description': utils.get_desc()}
    return render_to_response('blog-sitemap.html', info)


def get_details(request, blog_id):
    '''
    获取博客详情
    :param request:
    :param blog_id:
    :return:
    '''
    logger = logging.getLogger('app')

    try:
        blog = Blog.objects.get(id=blog_id, isDelete=False)
        blog.read += 1
        blog.save()

        Viewlog.objects.create(userId=request.session.get('uid', 0), ip=utils.getIP(request), blog_id=blog.id).save()

    except Blog.DoesNotExist:
        logger.info('blog does not exist, blog_id=%s' % blog_id)
        # return Http404
        return render_to_response('blog-sitemap.html', {'description': utils.get_desc()})

    if request.method == 'POST':  # 若为POST请求
        form = CommentForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            cleaned_data['blog'] = blog
            uid = request.session.get('uid', default=0)
            cleaned_data['userId'] = uid
            Comment.objects.create(**cleaned_data)

            user_name = "匿名用户"
            if uid != 0:
                user_name = User.objects.get(id=uid).name
            blog_title = blog.title
            send_email.delay([MAIL_USER],
                             user_name,
                             '<{user_name}>评论博客<{blog_title}>'.format(
                                 user_name=user_name, blog_title=blog_title),
                             cleaned_data['content'])

        # redirect('/detail', blog_id=blog_id)
        # redirect('/detail/{}'.format(blog_id))
        # HttpResponseRedirect('/detail/{}'.format(blog_id))
        return HttpResponseRedirect(reverse('blog_get_detail', args=[blog_id, ]))

    form = CommentForm()
    # 评论
    comments = blog.comment_set.all().order_by('-created')
    blog.conum = comments.count()

    tags_all = utils.get_tags_dict()
    if blog.id in tags_all:
        blog.alltags = tags_all[blog.id]
    else:
        blog.alltags = utils.get_tags_dict(True)[blog.id]

    for i in range(len(comments)):
        comments[i].floor = '#%d楼' % (len(comments) - i)
        if comments[i].userId:
            comments[i].userName = User.objects.get(id=comments[i].userId).name
        else:
            comments[i].userName = '匿名用户'

    ctx = {
        'title': blog.title,
        'description': utils.get_desc(blog.id),
        'blog': blog,
        'comments': comments,
        'form': form,
    }
    return render(request, 'blog-details.html', ctx)


# 用户信息页面在登出后不能继续用缓存页面, 而要刷新
# 使用@vary_on_cookie装饰器 --> 也无法达到效果
# @vary_on_cookie
def user_login(request):
    '''
    用户登录
    :param request:
    :return:
    '''
    if request.method == 'POST':
        account = request.POST.get('account')
        password0 = request.POST.get('password')
        password = utils.gainCipher(password0)

        user = User.objects.all()

        user = user.extra(
            where=['email="' + account + '" or phone="' + account + '"'])
        if user and len(user) == 1:
            if user[0].loginFailed >= 5:
                # 返回提示, 输入错误密码次数过多, 账户已锁定
                return render(request, 'login.html',
                              {'error': '输入错误密码次数过多, 账户已锁定', 'description': utils.get_desc()})

            if password == user[0].password:
                # 写入Session
                request.session['uid'] = user[0].id
                request.session['account'] = user[0].name
                request.session['email'] = user[0].email
                request.session['phone'] = user[0].phone
                request.session.set_expiry(18000)  # session过期时间 5小时

                # 记录日志
                Loginlog.objects.create(classify=1, ip=utils.getIP(request),
                                        user=user[0])
                # loginfailed = 0
                user = User.objects.extra(where=[
                    'email="' + account + '" or phone="' + account + '"']).get()
                user.loginFailed = 0
                user.save()

                # 登录成功后调整回去的页面
                next = request.POST.get('next')
                if not next or next == '':
                    next = '/'
                return redirect(next)
            else:
                user = User.objects.extra(where=[
                    'email="' + account + '" or phone="' + account + '"']).get()
                user.loginFailed += 1
                user.save()

                logger = logging.getLogger('app')
                logger.info('登录失败, 账户=%s,密码=%s' % (account, password0))

                return render(request, 'login.html', {'error': '用户名或密码错误', 'description': utils.get_desc()})
        else:
            return render(request, 'login.html', {'error': '用户名或密码错误', 'description': utils.get_desc()})

    else:
        if request.session.get('verify'):
            del request.session['verify']
        return render(request, 'login.html', {'next': request.GET.get('next'), 'description': utils.get_desc()})


def user_regist(request):
    '''
    用户注册
    :param request:
    :return:
    '''
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = utils.gainCipher(request.POST.get('password'))

        user = User.objects.filter(Q(email=email) | Q(phone=phone))
        if user or len(user) > 0:
            # 返回提示, 此邮箱和电话已注册
            return render(request, 'regist.html', {'error': '此邮箱或电话已注册', 'description': utils.get_desc()})
        else:
            User.objects.create(name=name, email=email, phone=phone,
                                password=password, creatIp=utils.getIP(request))
            # send_email.send_email_async([email], name, '注册成功', '恭喜您成功注册网站用户!')  # 线程发送邮箱
            send_email.delay([email], name, '注册成功',
                             '恭喜您成功注册网站用户!')  # mq + celery 发送邮件
            return render(request, 'login.html', {'error': '注册成功, 请登录!', 'description': utils.get_desc()})

    else:
        return render(request, 'regist.html', {'description': utils.get_desc()})


def user_info(request):
    """
    用户信息
    :param request:
    :return:
    """
    if request.session.get('uid'):
        id = request.session['uid']
        user = User.objects.get(id=id)

        login_time = user.loginlog_set.order_by('-created')
        user.login_time = login_time[0].created

        return render(request, 'user-info.html', {'user': user, 'description': utils.get_desc()})
    else:
        return render(request, 'login.html', {'description': utils.get_desc()})


# @vary_on_cookie
def user_logout(request):
    '''
    用户登出
    :param request:
    :return:
    '''
    if request.session.get('uid'):
        user = User.objects.get(id=request.session.get('uid'))
        Loginlog.objects.create(classify=2, ip=utils.getIP(request), user=user)
        del request.session['uid']
        del request.session['account']
        del request.session['email']
        del request.session['phone']

    nextUrl = '/'
    return redirect(nextUrl)


def user_reset(request):
    """
    重置密码
    :param request:
    :return:
    """
    remarks = ''
    if request.method == 'POST':
        if request.session.get('uid'):
            oldpasswd = request.POST.get('oldpasswd')
            newpasswd1 = request.POST.get('newpasswd1')
            newpasswd2 = request.POST.get('newpasswd2')
            if newpasswd1 == newpasswd2:
                user = User.objects.get(id=request.session['uid'])
                if user.password == utils.gainCipher(oldpasswd):
                    user.password = utils.gainCipher(newpasswd1)
                    user.loginFailed = 0
                    user.save()
                    return render(request, 'user-info.html', {'description': utils.get_desc()})
                else:
                    remarks = '原密码错误!'
            else:
                remarks = '两次输入的新密码不一致!'
        else:
            return render(request, 'login.html', {'description': utils.get_desc()})

    return render(request, 'reset-passwd.html', {'remarks': remarks, 'description': utils.get_desc()})


def user_forget(request):
    """
    用户忘记密码
    :param request:
    :return:
    """
    if request.method == 'POST':
        if request.POST.get('email'):
            email = request.POST['email']
            users = User.objects.filter(email=email)
            if users and len(users) > 0:
                user = users[0]

                # 将验证码存入db
                verify = VerifyCode.objects.create(user=user)
                verify.code = str(random.randint(100000, 999999))
                verify.email = email
                verify.ip = utils.getIP(request)
                verify.save()

                # send_email.send_email_async(email, user.name, '重置密码验证码', '您的验证码为%s' % verify.code)
                send_email.delay([email], user.name, '重置密码验证码',
                                 '您的验证码为%s' % verify.code)
                request.session['verify'] = user.email
                return render(request, 'forget-passwd1.html',
                              {'remarks': '已发送验证码', 'description': utils.get_desc()})
            else:
                return render(request, 'forget-passwd0.html',
                              {'remarks': '账号库找不到此邮箱, 请确认!', 'description': utils.get_desc()})
        elif request.POST.get('verification'):
            if request.session.get('verify'):
                code = request.POST['verification']
                verifys = VerifyCode.objects.all(). \
                    filter(email=request.session.get('verify'), success=False). \
                    filter(verifyFailed__lt=10). \
                    order_by('-created'). \
                    filter(created__range=[
                    (timezone.now() - timezone.timedelta(minutes=30)),
                    timezone.now()])
                if verifys and len(verifys) > 0:
                    verify = verifys[0]
                    if code == verify.code:
                        verify.success = True
                        verify.save()
                        request.session['verify_success'] = "success"
                        return render(request, 'forget-passwd2.html',
                                      {'remarks': '', 'description': utils.get_desc()})
                    else:
                        verify.verifyFailed += 1
                        verify.save()
                        return render(request, 'forget-passwd1.html',
                                      {'remarks': '验证码错误 ! ', 'description': utils.get_desc()})
                else:
                    return render(request, 'forget-passwd0.html',
                                  {'remarks': '验证码已失效, 需重新发送!', 'description': utils.get_desc()})

            else:
                return render(request, 'forget-passwd0.html',
                              {'remarks': '验证码已过期, 需重新发送!', 'description': utils.get_desc()})

        elif request.POST.get('newpasswd1'):
            passwd1 = request.POST['newpasswd1']
            passwd2 = request.POST['newpasswd2']
            if passwd1 != passwd2:
                return render(request, 'forget-passwd2.html',
                              {'remarks': '两次输入的新密码不一致!', 'description': utils.get_desc()})

            if request.session.get('verify') and request.session.get(
                    'verify_success') == 'success':
                verifys = VerifyCode.objects.all(). \
                    filter(email=request.session.get('verify'), success=True). \
                    filter(verifyFailed__lt=10). \
                    order_by('-created'). \
                    filter(created__range=[
                    (timezone.now() - timezone.timedelta(minutes=30)),
                    timezone.now()])
                if verifys and len(verifys) > 0:
                    user = \
                        User.objects.filter(
                            email=request.session.get('verify'))[0]
                    user.password = utils.encryption.gainCipher(passwd1)
                    user.loginFailed = 0
                    user.save()
                    del request.session['verify']
                    del request.session['verify_success']
                    return render(request, 'login.html', {'description': utils.get_desc()})
                else:
                    return render(request, 'forget-passwd0.html',
                                  {'remarks': '验证码已过期, 需重新发送!', 'description': utils.get_desc()})
            else:
                return render(request, 'forget-passwd0.html',
                              {'remarks': '验证码已过期, 需重新发送!', 'description': utils.get_desc()})

    if request.session.get('verify_success'):
        return render(request, 'forget-passwd2.html', {'remarks': '', 'description': utils.get_desc()})

    if request.session.get('verify'):
        return render(request, 'forget-passwd1.html', {'remarks': '', 'description': utils.get_desc()})

    return render(request, 'forget-passwd0.html', {'remarks': '', 'description': utils.get_desc()})


@csrf_exempt
def upload_image(request, dir_name):
    """
    kindeditor图片上传:
    返回 :
     {"error": 1, "message": "出错信息"}
     {"error": 0, "url": "图片地址"}
    :param request:
    :param dir_name:
    :return:
    """
    result = {"error": 1, "message": "上传出错"}
    files = request.FILES.get("imgFile", None)
    if files:
        result = uploads.image_upload(files, dir_name)
        response = HttpResponse(json.dumps(result),
                                content_type="application/json")
        response['X-Frame-Options'] = "SAMEORIGIN"  #
    return response
