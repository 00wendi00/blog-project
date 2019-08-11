#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : send_email.py
# @Author: Wade Cheung
# @Date  : 2018/7/28
# @Desc  : 发送邮件


import logging
from threading import Thread

import smtplib
from django.conf import settings
from email.mime.text import MIMEText
from email.header import Header


def send_email_async_mq(receivers, name, subject, content):
    """
    rabbitmq + celery
    :param receivers:
    :param name:
    :param subject:
    :param content:
    :return:
    """
    return __send_email(receivers, name, subject, content)


def send_email_async(receivers, name, subject, content):
    """
    线程, 异步发送邮件
    :param receivers:
    :param name:
    :param subject:
    :param content:
    :return:
    """
    thr = Thread(target=__send_email, args=[receivers, name, subject, content])
    thr.start()


def __send_email(receivers, name, subject, content):
    """

    :param receivers: 接受者的邮箱, 一个[]
    :param name: 接受者姓名
    :param subject: 主题
    :param content: 正文
    :return:
    """
    # 第三方 SMTP 服务
    mail_host = settings.MAIL_HOST  # 设置服务器
    mail_user = settings.MAIL_USER  # 用户名
    mail_pass = settings.MAIL_PASS  # 口令

    sender = mail_user

    message = MIMEText(content, 'plain', 'utf-8')
    # 无法解决发件人在outlook显示乱码问题
    message['From'] = '%s<%s>' % (Header('张文迪的博客网站', 'utf-8'), mail_user)
    message['To'] = Header(name)  # head中的收件人
    message['Subject'] = Header(subject)

    logger = logging.getLogger('app')
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, settings.MAIL_PORT)
        # smtpObj.set_debuglevel(1)     输出调试信息
        # smtpObj.ehlo()
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        # print("邮件发送成功")
        return 'success' + str(receivers) + name + subject + content
    except smtplib.SMTPException as e:
        # print(e, "Error: 无法发送邮件")
        logger.error('无法发送邮件,原因%s' % e)

    return 'failed' + str(receivers) + name + subject + content
