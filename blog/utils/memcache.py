#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : memcache.py
# @Author: Wade Cheung
# @Date  : 2019/8/9
# @Desc  :


from django.core.cache import cache

from blog.models import Tag


def get_tags_dict():
    # cache tags
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
