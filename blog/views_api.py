#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : views_api.py
# @Author: Wade Cheung
# @Date  : 2018/8/9
# @Desc  :


from rest_framework import viewsets

from blog.models import Tag, Catagory
from blog.serializers import TagSerializer, CatagorySerializer


class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Tag.objects.all().order_by('-id')
    serializer_class = TagSerializer


class CatagoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Catagory.objects.all()
    serializer_class = CatagorySerializer
