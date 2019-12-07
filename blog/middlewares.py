#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : middlewares.py
# @Author: Wade Cheung
# @Date  : 2019/12/7
# @Desc  : 黑名单返回404

import logging

from django.http import Http404
from django.utils.deprecation import MiddlewareMixin

from blog.models import Blacklist
from blog.utils.utils import getIP


class BlacklistMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = getIP(request)

        blacklist = Blacklist.objects.all()
        for blackip in blacklist:
            if ip == blackip.ip:
                logger = logging.getLogger('app')
                logger.info(f"ip黑名单限制访问, {blackip.ip}, {blackip.remark}")
                raise Http404
