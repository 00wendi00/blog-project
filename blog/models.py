from django.db import models


# Create your models here.
class Catagory(models.Model):
    """
    博客分类
    """
    name = models.CharField('分类', max_length=50, blank=False)
    remark = models.CharField('描述', max_length=50, blank=False)
    isDelete = models.BooleanField('是否删除', default=False)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    博客标签
    """
    name = models.CharField('标签', max_length=50, blank=False)
    remark = models.CharField('描述', max_length=50, blank=False)
    isDelete = models.BooleanField('是否删除', default=False)

    def __str__(self):
        return self.name


class Blog(models.Model):
    """
    博客
    """
    title = models.CharField('标题', max_length=200)
    intro = models.CharField('简介', max_length=200)
    author = models.CharField('作者', max_length=50)
    content = models.TextField('博客正文')
    created = models.DateTimeField('发布时间', auto_now_add=True, )
    read = models.IntegerField('阅读量', default=0)
    catagory = models.ForeignKey("Catagory", verbose_name='分类',
                                 on_delete=models.CASCADE)  # verbose_name = ''
    tags = models.ManyToManyField("Tag", verbose_name='标签')
    isDraft = models.BooleanField('是否是草稿', default=True)
    isDelete = models.BooleanField('是否删除', default=False)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    游客或用户评论
    """
    blog = models.ForeignKey("Blog", on_delete=models.CASCADE)
    userId = models.IntegerField('用户id', default=0)
    content = models.CharField('内容', max_length=500)
    created = models.DateTimeField('发布时间', auto_now_add=True, )
    isDelete = models.BooleanField('是否删除', default=False)

    def __str__(self):
        return self.content


class User(models.Model):
    """
    用户
    """
    name = models.CharField('姓名', max_length=50, null=False)
    email = models.CharField('邮箱', max_length=50, null=False)
    phone = models.CharField('电话', max_length=50, null=False)
    password = models.CharField('密码', max_length=50, null=False)
    loginFailed = models.IntegerField('登录失败次数', default=0)
    created = models.DateTimeField('注册时间', auto_now_add=True, )
    creatIp = models.CharField('ip地址', max_length=20, null=True)


class Loginlog(models.Model):
    """
    登录日志
    """
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    classify = models.IntegerField('分类1为登录,2为登出', default=1)
    created = models.DateTimeField('登录登出时间', auto_now_add=True, )
    ip = models.CharField('ip地址', max_length=20, null=True)


class Viewlog(models.Model):
    """
    查看博客日志
    """
    blog = models.ForeignKey(Blog, verbose_name='博客', on_delete=models.CASCADE)
    userId = models.IntegerField('用户id', default=0)
    created = models.DateTimeField('查看时间', auto_now_add=True, )
    ip = models.CharField('ip地址', max_length=20, null=True)


class VerifyCode(models.Model):
    """
    验证码
    """
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    created = models.DateTimeField('查看时间', auto_now_add=True)
    email = models.CharField('邮箱', max_length=50, null=True)
    code = models.CharField('验证码', max_length=20, null=True)
    verifyFailed = models.IntegerField('验证失败次数', default=0)
    success = models.BooleanField('是否验证成功', default=False)
    ip = models.CharField('ip地址', max_length=20, null=True)


class Blacklist(models.Model):
    """
    ip黑名单
    """
    ip = models.CharField('ip地址', max_length=50, null=False)
    remark = models.CharField('描述', max_length=50, null=True)
    created = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return self.ip
