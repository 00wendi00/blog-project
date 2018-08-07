一. 部署生产环境注意修改
ALLOWED_HOSTS
DEBUG = False
数据库连接
日志记录的地址
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True


# 生产环境下, https://www.hiwendi.com/
# 开发环境下, http://127.0.0.1:8000
