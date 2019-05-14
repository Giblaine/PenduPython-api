#! /usr/bin/python
# -*- coding:utf-8 -*-

import pymysql.cursors

def connect():
    connection = pymysql.connect(host='bu2xiutdf3xdkdrkrwtc-mysql.services.clever-cloud.com',
                                 user='uoa979ile07jysko',
                                 password='OS8Yn5M1iHbuIYzoz1cy',
                                 db='bu2xiutdf3xdkdrkrwtc',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection