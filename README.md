## 个人博客源码
地址: https://www.hiwendi.com/

测试api: https://www.hiwendi.com/api/

RabbitMQ: http://120.78.176.222:15672/#/

### 一.说明

#### 环境Python3.6.4, Django==2.1.11; djangorestframework==3.9.1; 系统环境ubuntu14.04, uwsgi, Nginx, mysql
#### 使用技术

RabbitMQ

celery

https

bootstrap

kindeditor + 图片和附件上传下载

admin

cache

threading --> 异步发送邮件

hashlib.md5

logging


#### 相关文件

nginx配置文件, uwsgi配置文件, requirements文件

mysite_nginx.conf

myweb_uwsgi.ini

requirements.txt


#### 待实现 :

背景


### 二. 部署生产环境注意修改settings.py

ALLOWED_HOSTS

DEBUG = False

数据库连接

日志记录的地址

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True


### 三. 问题汇总
##### 1, 由于安全问题, 将Django升级到2.2.9版本, mysqlclient报错
```
django.core.exceptions.ImproperlyConfigured: mysqlclient 1.3.13 or newer is required; you have 0.9.2.
unable to load app 0 (mountpoint='') (callable not found or import error)
```

```python
# 解决 : 
# 找到Python环境下 django包，并进入到db/backends下的mysql文件夹
# 1, 找到base.py文件，注释掉 base.py 中如下部分（35/36行）
if version < (1, 3, 3):
     raise ImproperlyConfigured("mysqlclient 1.3.3 or newer is required; you have %s" % Database.__version__)


# 2, 找到operations.py文件（146行），将decode改为encode
if query is not None:
    query = query.decode(errors='replace')
return query
#改为
if query is not None:
    query = query.encode(errors='replace')
return query
```
