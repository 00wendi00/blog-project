from django.contrib import admin
from blog.models import *


# Register your models here.
#  让系统管理员能对注册的这些模型进行管理
# admin.site.register([Catagory, Tag, Comment, User, Loginlog])

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'intro', 'created', 'read')
    filter_horizontal = ('tags',)

    class Media:
        js = (
            'js/kindeditor/kindeditor-all.js',
            'js/kindeditor/lang/zh-CN.js',
            'js/kindeditor/config.js',
        )


@admin.register(Catagory)
class CatagoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'remark')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'remark')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        """  重新定义此函数，限制普通用户所能修改的字段  """
        # if request.user.is_superuser:
        #     self.readonly_fields = []
        return self.readonly_fields

    list_display = ('blog', 'userId', 'content', 'created')
    readonly_fields = ('blog', 'userId', 'content', 'created')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        """  重新定义此函数，限制普通用户所能修改的字段  """
        # if request.user.is_superuser:
        #     self.readonly_fields = []
        return self.readonly_fields

    list_display = ('name', 'email', 'phone', 'password', 'created', 'creatIp')
    readonly_fields = ('name', 'email', 'phone', 'password', 'created', 'creatIp')


@admin.register(Loginlog)
class LoginlogAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        """  重新定义此函数，限制普通用户所能修改的字段  """
        # if request.user.is_superuser:
        #     self.readonly_fields = []
        return self.readonly_fields

    list_display = ('user', 'classify', 'created', 'ip')
    readonly_fields = ('user', 'classify', 'created', 'ip')


@admin.register(Viewlog)
class ViewlogAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        """  重新定义此函数，限制普通用户所能修改的字段  """
        if request.user.is_superuser:
            self.readonly_fields = []
        return self.readonly_fields

    list_display = ('blog', 'userId', 'created', 'ip')
    readonly_fields = ('blog', 'userId', 'created', 'ip')
