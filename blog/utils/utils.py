#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : utils.py
# @Author: Wade Cheung
# @Date  : 2019/8/11
# @Desc  : get ip; encrypt; 缓存和获取所有博客的tags


from blog.models import Tag

from hashlib import md5
from django.conf import settings
from django.core.cache import cache


def getIP(request):
    """
    get request ip
    :param request:
    :return:
    """
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']

    return ip


def gainCipher(password, salt=settings.MD5_SALT):
    """
    密码加盐加密
    :param password:
    :param salt:
    :return:
    """
    if password:
        m1 = md5()
        m1.update(password.encode('utf-8'))
        p = m1.hexdigest()
        m2 = md5()
        m2.update((p + salt).encode('utf-8'))  # 加盐
        p = m2.hexdigest()
        return p

    return None


def get_tags_dict(new=False):
    """
    缓存和获取所有博客的tags
    :return: {'blog_id':'tag1 tag2'}
    """
    if new:
        tags_dict = None
    else:
        tags_dict = cache.get('tags_dict')

    if not tags_dict:
        tags_list = Tag.objects.all().values_list('blog', 'blog__tags__name')
        tags_dict = {}
        for item in tags_list:
            if item[0] in tags_dict:
                if item[1] not in tags_dict[item[0]]:
                    tags_dict[item[0]].append(item[1])
            elif item[0]:
                tags_dict[item[0]] = [item[1]]

        tags_dict = {key: ' '.join(tags_dict[key]) for key in tags_dict}
        cache.set('tags_dict', tags_dict, 3600 * 24 * 30)

    return tags_dict
