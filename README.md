# 个人博客源码
https://www.hiwendi.com/

## 一.说明

### 环境Python3.6.4, Django2.0.7; 系统环境ubuntu14.04, uwsgi, Nginx, mysql


### 使用技术

https

bootstrap

kindeditor

admin

cache

threading --> 异步发送邮件

hashlib.md5

logging


### 相关文件

nginx配置文件, uwsgi配置文件, requir文件

mysite_nginx.conf

myweb_uwsgi.ini

requirements.txt


## 二. 部署生产环境注意修改settings.py

ALLOWED_HOSTS

DEBUG = False

数据库连接

日志记录的地址

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True


### 生产环境下, https://www.hiwendi.com/
### 开发环境下, http://127.0.0.1:8000
