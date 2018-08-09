#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : serializers.py
# @Author: Wade Cheung
# @Date  : 2018/8/9
# @Desc  :

from rest_framework import serializers
from blog.models import Tag, Catagory


class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'remark', 'isDelete')


class CatagorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Catagory
        fields = ('id', 'name', 'remark', 'isDelete')
