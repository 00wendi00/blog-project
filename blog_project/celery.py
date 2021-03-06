#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : celery.py
# @Author: Wade Cheung
# @Date  : 2018/9/2
# @Desc  :


from __future__ import absolute_import

import os

from celery import Celery, platforms, shared_task
from django.conf import settings

# set the default Django settings module for the 'celery' program.
from blog.utils.send_email import send_email_async_mq

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')

app = Celery('blog')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# 可以用root账号启动
platforms.C_FORCE_ROOT = True


@shared_task
def send_email(receivers, name, subject, content):
    return send_email_async_mq(receivers, name, subject, content)

