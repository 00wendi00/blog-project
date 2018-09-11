#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : tasks.py
# @Author: Wade Cheung
# @Date  : 2018/9/2
# @Desc  :


from __future__ import absolute_import
from celery import shared_task

from blog.utils.send_email import send_email_async_mq


@shared_task
def send_email(receivers, name, subject, content):
    return send_email_async_mq(receivers, name, subject, content)