#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : encryption.py
# @Author: Wade Cheung
# @Date  : 2018/7/27
# @Desc  : md5加盐加密 . md5(md5(password) + salt)

from hashlib import md5
from django.conf import settings


def gainCipher(password, salt=settings.MD5_SALT):
    if password:
        m1 = md5()
        m1.update(password.encode('utf-8'))
        p = m1.hexdigest()
        m2 = md5()
        m2.update((p + salt).encode('utf-8'))  # 加盐
        p = m2.hexdigest()
        return p

    return None
