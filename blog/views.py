import json
import random
import logging

from django.http import Http404, HttpResponse
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import render, render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt

from blog.forms import CommentForm
from blog.models import *
from blog.utils import encryption, send_email, uploads
from blog import tasks


# @cache_page(60), 视图缓存无法判断是否登录
def get_blogs(request):
    '''
    获取博客列表
    :param request:
    :return:
    '''
    catagory = request.GET.get("catagory")
    tag = request.GET.get("tag")
    logger = logging.getLogger('app')
    try:
        if catagory:
            catagory = Catagory.objects.get(id=catagory)
            blogs = Blog.objects.all().order_by('-created').filter(isDelete=False, catagory=catagory)
        elif tag:
            tag = Tag.objects.get(id=tag)
            blogs = Blog.objects.all().order_by('-created').filter(isDelete=False, tags=tag)
        else:
            blogs = Blog.objects.all().order_by('-created').filter(isDelete=False)
    except Exception:
        logger.info('bloglist does not exist, catagory=%s, tag=%s' % (catagory, tag))
        raise Http404

    for blog in blogs:
        conum = blog.comment_set.count
        blog.conum = conum
        blog.alltags = blog.tags.all()[0].name
    if request.session.get('uid'):
        is_login = True
    else:
        is_login = False

    info = {'blogs': blogs, 'catagory': catagory, 'tag': tag, 'title': '张文迪的博客', 'is_login': is_login, }
    return render_to_response('blog-list.html', info)


def get_catagory(request):
    '''
    获取分类列表
    :param request:
    :return:
    '''
    catagorys = Catagory.objects.filter(isDelete=False)
    if request.session.get('uid'):
        is_login = True
    else:
        is_login = False

    info = {'catagorys': catagorys, 'title': '张文迪的博客分类', 'is_login': is_login, }
    return render_to_response('blog_catagory.html', info)


def get_tag(request):
    '''
    获取标签列表
    :param request:
    :return:
    '''
    tags = Tag.objects.filter(isDelete=False)
    if request.session.get('uid'):
        is_login = True
    else:
        is_login = False

    info = {'tags': tags, 'title': '张文迪的博客标签', 'is_login': is_login, }
    return render_to_response('blog_tag.html', info)


def get_details(request, blog_id):
    '''
    获取博客详情
    :param request:
    :param blog_id:
    :return:
    '''
    try:
        logger = logging.getLogger('app')
        blog = Blog.objects.get(id=blog_id)
        blog.read += 1
        blog.save()

        if request.session.get('uid'):
            Viewlog.objects.create(userId=request.session.get('uid'), ip=getIP(request), blog_id=blog.id).save()
        else:
            Viewlog.objects.create(ip=getIP(request), blog_id=blog.id).save()

    except Blog.DoesNotExist:
        logger.info('blog does not exist, blog_id=%s' % blog_id)
        return Http404
    if request.method == 'GET':  # 若为get请求
        form = CommentForm()
    else:
        form = CommentForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            cleaned_data['blog'] = blog

            if request.session.get('uid'):
                cleaned_data['userId'] = request.session['uid']
            Comment.objects.create(**cleaned_data)
        form = CommentForm()

    conum = blog.comment_set.count
    blog.conum = conum
    blog.alltags = blog.tags.all()[0].name

    if request.session.get('uid'):
        is_login = True
    else:
        is_login = False

    # 评论
    comments = blog.comment_set.all().order_by('-created')
    for i in range(len(comments)):
        comments[i].floor = '#%d楼' % (len(comments) - i)
        if comments[i].userId:
            comments[i].userName = User.objects.get(id=comments[i].userId).name
        else:
            comments[i].userName = '匿名用户'

    ctx = {
        'title': blog.title,
        'blog': blog,
        'comments': comments,
        'form': form,
        'is_login': is_login,
    }
    return render(request, 'blog-details.html', ctx)


def user_login(request):
    '''
    用户登录
    :param request:
    :return:
    '''
    if request.method == 'POST':
        account = request.POST.get('account')
        password0 = request.POST.get('password')
        password = encryption.gainCipher(password0)

        user = User.objects.all()

        user = user.extra(where=['email="' + account + '" or phone="' + account + '"'])
        if user and len(user) == 1:
            if user[0].loginFailed >= 5:
                # 返回提示, 输入错误密码次数过多, 账户已锁定
                return render(request, 'login.html', {'error': '输入错误密码次数过多, 账户已锁定'})

            if password == user[0].password:
                # 写入Session
                request.session['uid'] = user[0].id
                request.session['account'] = user[0].name
                request.session['email'] = user[0].email
                request.session['phone'] = user[0].phone
                request.session.set_expiry(18000)  # session过期时间 5小时

                # 记录日志
                Loginlog.objects.create(classify=1, ip=getIP(request), user=user[0])
                # loginfailed = 0
                user = User.objects.extra(where=['email="' + account + '" or phone="' + account + '"']).get()
                user.loginFailed = 0
                user.save()

                # 登录成功后调整回去的页面
                next = request.POST.get('next')
                if not next or next == '':
                    next = '/'
                return redirect(next)
            else:
                user = User.objects.extra(where=['email="' + account + '" or phone="' + account + '"']).get()
                user.loginFailed += 1
                user.save()

                logger = logging.getLogger('app')
                logger.info('登录失败, 账户=%s,密码=%s' % (account, password0))

                return render(request, 'login.html', {'error': '用户名或密码错误'})
        else:
            return render(request, 'login.html', {'error': '用户名或密码错误'})

    else:
        if request.session.get('verify'):
            del request.session['verify']
        return render(request, 'login.html', {'next': request.GET.get('next')})


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
        password = encryption.gainCipher(request.POST.get('password'))

        user = User.objects.filter(Q(email=email) | Q(phone=phone))
        if user or len(user) > 0:
            # 返回提示, 此邮箱和电话已注册
            return render(request, 'regist.html', {'error': '此邮箱或电话已注册'})
        else:
            User.objects.create(name=name, email=email, phone=phone, password=password, creatIp=getIP(request))
            # send_email.send_email_async([email], name, '注册成功', '恭喜您成功注册网站用户!')  # 线程发送邮箱
            tasks.send_email.delay([email], name, '注册成功', '恭喜您成功注册网站用户!')  # mq + celery 发送邮件
            return render(request, 'login.html', {'error': '注册成功, 请登录!'})

    else:
        return render(request, 'regist.html')


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

        return render(request, 'user-info.html', {'user': user, 'is_login': True})
    else:
        return render(request, 'login.html')


def user_logout(request):
    '''
    用户登出
    :param request:
    :return:
    '''
    if request.session.get('uid'):
        user = User.objects.get(id=request.session.get('uid'))
        Loginlog.objects.create(classify=2, ip=getIP(request), user=user)
        del request.session['uid']
        del request.session['account']
        del request.session['email']
        del request.session['phone']

    nextUrl = '/'
    return redirect(nextUrl)


def getIP(request):
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    return ip


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
                if user.password == encryption.gainCipher(oldpasswd):
                    user.password = encryption.gainCipher(newpasswd1)
                    user.loginFailed = 0
                    user.save()
                    return render(request, 'user-info.html')
                else:
                    remarks = '原密码错误!'
            else:
                remarks = '两次输入的新密码不一致!'
        else:
            return render(request, 'login.html')

    return render(request, 'reset-passwd.html', {'remarks': remarks, 'is_login': True})


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
                verify.ip = getIP(request)
                verify.save()

                # send_email.send_email_async(email, user.name, '重置密码验证码', '您的验证码为%s' % verify.code)
                tasks.send_email.delay(email, user.name, '重置密码验证码', '您的验证码为%s' % verify.code)
                request.session['verify'] = user.email
                return render(request, 'forget-passwd1.html', {'remarks': '已发送验证码', 'is_login': False})
            else:
                return render(request, 'forget-passwd0.html', {'remarks': '账号库找不到此邮箱, 请确认!', 'is_login': False})
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
                        return render(request, 'forget-passwd2.html', {'remarks': '', 'is_login': False})
                    else:
                        verify.verifyFailed += 1
                        verify.save()
                        return render(request, 'forget-passwd1.html', {'remarks': '验证码错误 ! ', 'is_login': False})
                else:
                    return render(request, 'forget-passwd0.html', {'remarks': '验证码已失效, 需重新发送!', 'is_login': False})

            else:
                return render(request, 'forget-passwd0.html', {'remarks': '验证码已过期, 需重新发送!', 'is_login': False})

        elif request.POST.get('newpasswd1'):
            passwd1 = request.POST['newpasswd1']
            passwd2 = request.POST['newpasswd2']
            if passwd1 != passwd2:
                return render(request, 'forget-passwd2.html', {'remarks': '两次输入的新密码不一致!', 'is_login': False})

            if request.session.get('verify') and request.session.get('verify_success') == 'success':
                verifys = VerifyCode.objects.all(). \
                    filter(email=request.session.get('verify'), success=True). \
                    filter(verifyFailed__lt=10). \
                    order_by('-created'). \
                    filter(created__range=[
                    (timezone.now() - timezone.timedelta(minutes=30)),
                    timezone.now()])
                if verifys and len(verifys) > 0:
                    user = User.objects.filter(email=request.session.get('verify'))[0]
                    user.password = encryption.gainCipher(passwd1)
                    user.loginFailed = 0
                    user.save()
                    del request.session['verify']
                    del request.session['verify_success']
                    return render(request, 'login.html')
                else:
                    return render(request, 'forget-passwd0.html', {'remarks': '验证码已过期, 需重新发送!', 'is_login': False})
            else:
                return render(request, 'forget-passwd0.html', {'remarks': '验证码已过期, 需重新发送!', 'is_login': False})

    if request.session.get('verify_success'):
        return render(request, 'forget-passwd2.html', {'remarks': '', 'is_login': False})

    if request.session.get('verify'):
        return render(request, 'forget-passwd1.html', {'remarks': '', 'is_login': False})

    return render(request, 'forget-passwd0.html', {'remarks': '', 'is_login': False})


@csrf_exempt
def upload_image(request, dir_name):
    ##################
    #  kindeditor图片上传返回数据格式说明：
    # {"error": 1, "message": "出错信息"}
    # {"error": 0, "url": "图片地址"}
    ##################
    result = {"error": 1, "message": "上传出错"}
    files = request.FILES.get("imgFile", None)
    if files:
        result = uploads.image_upload(files, dir_name)
        response = HttpResponse(json.dumps(result), content_type="application/json")
        response['X-Frame-Options'] = "SAMEORIGIN"  #
    return response
