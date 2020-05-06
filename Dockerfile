FROM python:3.6-stretch

# add a new user
#RUN useradd --create-home --no-log-init --shell /bin/bash blog
#RUN echo 'blog:blog' | chpasswd
WORKDIR /home/app/blog_project/

ADD ./requirements.txt ./
RUN pip install -r requirements.txt -i https://pypi.douban.com/simple

# 由于安全问题, 将Django升级到2.2.9版本, mysqlclient报错, 替换文件即可
ADD ./conf/base.py /usr/local/lib/python3.6/site-packages/django/db/backends/mysql/base.py
ADD ./conf/operations.py /usr/local/lib/python3.6/site-packages/django/db/backends/mysql/operations.py

RUN chmod -R 777 /home/app/blog_project/
RUN chmod -R 777 /var/log/
#USER blog
RUN export PYTHONPATH=./
