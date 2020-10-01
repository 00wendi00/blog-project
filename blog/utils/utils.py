#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : utils.py
# @Author: Wade Cheung
# @Date  : 2019/8/11
# @Desc  : get ip; encrypt; 缓存和获取所有博客的tags


import html
import re
from hashlib import md5
from django.conf import settings
from django.core.cache import cache

from blog.models import Tag, Blog, Catagory


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


def get_desc(blog_id=0):
    """
    缓存和获取所有description, 0存的是所有的title, 其他id存内容
    :return: {0:'all title', blog_id:'contet'}
    """
    desc_dict = cache.get('desc_dict')
    if not desc_dict or not desc_dict.get(blog_id):
        desc_dict = {}
        titles = '张文迪 博客 '
        tags = Tag.objects.all().filter(isDelete=False).values('name', 'remark')
        titles += ' '.join([tag['name'] + ' ' + tag['remark'] for tag in tags])
        categorys = Catagory.objects.all().filter(isDelete=False).values('name', 'remark')
        titles += ' '.join([category['name'] + ' ' + category['remark'] for category in categorys])

        blogs = Blog.objects.all().filter(isDraft=False, isDelete=False).values('id', 'title', 'content')
        for blog in blogs:
            titles += blog['title'] + ' '

            pattern = re.compile(r'<pre.*?>.*?</pre>', re.S)
            res = re.sub(pattern, '', blog['content'])
            if res:
                pattern = re.compile(r'<.*?>|\n|\r|\t|&nbsp;', re.S)
                res = re.sub(pattern, '', res)
                res = html.unescape(res).strip()
            desc_dict[blog['id']] = res or ' '

        desc_dict[0] = titles
        cache.set('desc_dict', desc_dict, 3600 * 24 * 30)
    return desc_dict[blog_id]
