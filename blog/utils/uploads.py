#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : uploads.py
# @Author: Wade Cheung
# @Date  : 2018/7/26
# @Desc  : 图片上传

# 参考, https://www.lijinlong.cc/django/djxs/2014.html
# 在目录创建处有修改


import os
import uuid
import datetime as dt
from blog_project import settings


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
    image_suffix = ['jpg', 'png', 'jpeg', 'gif', 'bmp']

    file_suffix = files.name.split(".")[-1]
    relative_path_file = upload_generation_dir(dir_name)
    path = os.path.join(settings.MEDIA_ROOT, relative_path_file)
    if not os.path.exists(path):  # 如果目录不存在创建目录
        os.makedirs(path)
    # 上传的是图片
    if file_suffix in image_suffix:
        file_name = str(uuid.uuid1()) + "." + file_suffix
        path_file = os.path.join(path, file_name)
        file_url = settings.MEDIA_URL + relative_path_file + '/' + file_name
        open(path_file, 'wb').write(files.file.read())
        return {"error": 0, "url": file_url}
    else:
        # 上传的是附件
        file_name = files.name
        path_file = os.path.join(path, file_name)
        open(path_file, 'wb').write(files.file.read())
        return {"error": 0,
                "url": settings.MEDIA_URL + relative_path_file + '/' + files.name,
                'filename': files.name}
