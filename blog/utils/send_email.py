#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : send_email.py
# @Author: Wade Cheung
# @Date  : 2018/7/28
# @Desc  : gmail发送邮件
import smtplib
from threading import Thread
from email.mime.text import MIMEText
from email.header import Header
from django.conf import settings


def send_email_async(receivers, name, subject, content):
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
    message['From'] = Header(settings.MAIL_HEADER, 'utf-8')
    message['To'] = Header(name, 'utf-8')  # head中的收件人
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP(mail_host, settings.MAIL_PORT)
        # smtpObj.set_debuglevel(1)     输出调试信息
        # smtpObj.ehlo()
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        # print("邮件发送成功")
    except smtplib.SMTPException as e:
        print(e, "Error: 无法发送邮件")
