#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : uploads.py
# @Author: Wade Cheung
# @Date  : 2018/7/26
# @Desc  : 图片上传

# 参考, https://www.lijinlong.cc/django/djxs/2014.html
# 在目录创建处有修改


from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import os
import uuid
import json
import datetime as dt

from blog_project import settings


@csrf_exempt
def upload_image(request, dir_name):
    ##################
    #  kindeditor图片上传返回数据格式说明：
    # {"error": 1, "message": "出错信息"}
    # {"error": 0, "url": "图片地址"}
    ##################
    result = {"error": 1, "message": "上传出错"}
    files = request.FILES.get("imgFile", None)
    if files:
        result = image_upload(files, dir_name)
        response = HttpResponse(json.dumps(result), content_type="application/json")
        response['X-Frame-Options'] = "SAMEORIGIN"  #
    return response


# 目录创建
def upload_generation_dir(dir_name):
    today = dt.datetime.today()
    # dir_name = dir_name + '/%d%d==' % (today.year, today.month)
    if not os.path.exists(settings.MEDIA_ROOT + '/' + dir_name):
        os.makedirs(settings.MEDIA_ROOT + '/' + dir_name)
    return dir_name


# 图片上传
def image_upload(files, dir_name):
    # 允许上传文件类型
    allow_suffix = ['jpg', 'png', 'jpeg', 'gif', 'bmp']
    file_suffix = files.name.split(".")[-1]
    if file_suffix not in allow_suffix:
        return {"error": 1, "message": "图片格式不正确"}
    relative_path_file = upload_generation_dir(dir_name)
    path = os.path.join(settings.MEDIA_ROOT, relative_path_file)
    if not os.path.exists(path):  # 如果目录不存在创建目录
        os.makedirs(path)
    file_name = str(uuid.uuid1()) + "." + file_suffix
    path_file = os.path.join(path, file_name)
    file_url = settings.MEDIA_URL + relative_path_file + '/' + file_name
    open(path_file, 'wb').write(files.file.read())
    return {"error": 0, "url": file_url}
