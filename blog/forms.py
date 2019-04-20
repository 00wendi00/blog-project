#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : forms.py
# @Author: Wade Cheung
# @Date  : 2018/7/26
# @Desc  :
from django import forms


class CommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(
        attrs={'class': "form-control", 'placeholder': u"请在此填写评论",
               'cols': '100', 'rows': '3'}), label='评论内容', required=True,
        max_length=200, help_text='限制200字',
        error_messages={'required': u'请填写您的评论内容!', }, )
