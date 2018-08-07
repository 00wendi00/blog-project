"""blog_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.views import static
from django.views.generic import RedirectView

from blog.views import *
from blog_project import settings
from blog.utils.uploads import upload_image

urlpatterns = [
    url('admin/', admin.site.urls),
    url(r'^favicon.ico$', RedirectView.as_view(url=r'static/favicon.ico')),
    url(r'^$', get_blogs),
    url(r'^blogs/$', get_blogs),
    url(r'^detail/(\d+)/$', get_details, name='blog_get_detail'),
    url(r"^upload/(?P<path>.*)$", static.serve, {"document_root": settings.MEDIA_ROOT, }),
    url(r'^admin/upload/(?P<dir_name>[^/]+)$', upload_image, name='upload_image'),

    url(r'^catagory/$', get_catagory),
    url(r'^tag/$', get_tag),

    url(r'^user/info/$', user_info),
    url(r'^user/login/$', user_login),
    url(r'^user/logout/$', user_logout),
    url(r'^user/regist/$', user_regist),
    url(r'^user/reset/$', user_reset),
    url(r'^user/forget/$', user_forget),
]
