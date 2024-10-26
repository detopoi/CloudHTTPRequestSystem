# coding: utf-8

import os
import datetime
import pickle
import sqlite3
import string
import subprocess
import random
import json
import logging
import zipfile
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from io import BytesIO
from urllib.parse import parse_qs
from urllib.parse import urlsplit


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"

logging.basicConfig(
    filename='my.log',
    level=logging.DEBUG,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT)

conn = sqlite3.connect(':memory:')
cursor = conn.cursor()
cursor.execute('create table user (user_id varchar(256) primary key, all_info TEXT)')


def add_user_to_db(user_id, data):
    cursor = conn.cursor()
    cursor.execute('insert into user (user_id, all_info) values ({}, \"{}\")'.format(user_id, data))

def query_user_id_from_db(user_id):
    cursor.execute('select * from user where user_id=%s' % str(user_id))
    values = cursor.fetchall()
    if values:
        return values[0][0]
    return None


class UserInfo():
    def __init__(self, usr_info):
        self.name = usr_info['name']
        self.user_id = usr_info['user_id']
        self.username = usr_info['username']
        self.password = usr_info['password']
        self.email = usr_info['email']
        self.phone_number = usr_info['phone_number']
        self.description = usr_info['description']

    def class_to_dict(self):
        return {'name': self.name, 'user_id': self.user_id, 'user_name': self.username, 'email': self.email,
                'phone_number': self.phone_number, 'description': self.description}


class MaintainBiz():

    @staticmethod
    def register_user(**user_info):
        """ 自助注册新用户

        @param user_info 用户信息
        @return 注册成功与否
        """
        fp = None
        response = {'status': 'success', 'message': ''}
        try:
            logging.info('register user info {}'.format(user_info))
            today_str = datetime.date.today().strftime('%Y%m%d')
            num_random = ''.join(random.sample(string.digits, 8))
            user_id = ''.join([today_str, num_random])
            user_info['user_id'] = user_id
            u_info_instance = UserInfo(user_info)
            data_str = pickle.dumps(u_info_instance)
            add_user_to_db(user_id, data_str)
            file_path = os.path.join('all_user_info', 'USER-{}.json'.format(user_id))
            fp = open(file_path, 'wb+')
            fp.write(data_str)
            fp.close()
        except Exception as e:
            msg = 'register user failed: {}'.format(e)
            response = {'status': 'fail', 'message': msg}
        finally:
            if fp:
               fp.close()
        return response

    @staticmethod
    def query_user_info(user_id):
        """ 查询用户信息

        @param user_id 用户ID
        @return 用户信息详情
        """
        db_user_id = query_user_id_from_db(user_id)
        if not db_user_id:
            return ''
        file_path = os.path.join('all_user_info', 'USER-{}.json'.format(db_user_id))
        fp = open(file_path, 'rb+')
        data = pickle.load(fp)
        fp.close()
        return data.class_to_dict()

    @staticmethod
    def upload_result(stdoutdata, stderrdata, url):
        # 脚本执行结果上传
        if not url:
            return True
        result = "result output:{}, error:{}".format(stdoutdata, stderrdata)
        fp = open('result.log', 'w+')
        fp.write(result)
        fp.close()
        cmd = 'curl --form "file=@result.log" {}'.format(url)
        p = subprocess.Popen(args=cmd, shell=True)
        stdoutdata, stderrdata = p.communicate()
        ret = p.returncode
        if ret:
            return False
        return True

    @staticmethod
    def process_maintain_script(**kwargs):
        """ 执行运维任务

        @param kwargs 待执行的运维脚本，脚本参数, 执行用户 {'script_name':xxxx, 'args': ['yyy', 'zzz'], 'user_id': id}
        @return 成功与否 {'status': 'success/fail', 'message': 'failed reason'}
        """
        script_name = kwargs.get('script_name', '')
        args = kwargs.get('args', '')
        url = kwargs.get('callback_url', '')
        cmd = '{} {}'.format(script_name, ' '.join(args))
        p = subprocess.Popen(args=cmd, shell=True)
        stdoutdata, stderrdata = p.communicate()
        ret = p.returncode
        if not ret and MaintainBiz.upload_result(stdoutdata, stderrdata, url):
            return {'status': 'success', 'message':''}
        else:
            return {'status': 'fail', 'message':'{}'.format(stderrdata)}


    @staticmethod
    def upload_script(**kwargs):
        """ 上传运维script脚本

        @param kwargs  {'script_name':xxxx, 'user_id': id}
        @return 成功与否
        """
        file_path = 'test.zip'
        des_dir = '.'
        src_file = zipfile.ZipFile(file_path, 'r')
        src_file.extractall(des_dir)
        return {'status': 'success', 'message': ''}


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    func_map = {'/register_user': MaintainBiz.register_user,
                '/query_user_info': MaintainBiz.query_user_info,
                '/process_maintain_script': MaintainBiz.process_maintain_script,
                '/upload_script': MaintainBiz.upload_script}

    def do_GET(self):
        url_result = urlsplit(self.path)
        url_path = url_result.path
        query_info_dict = parse_qs(url_result.query)
        user_id = query_info_dict.get('user_id')[0]
        func = self.func_map.get(url_path, None)
        response = BytesIO()
        if func and user_id:
            json_data = func(user_id)
            response.write(bytes(json.dumps(json_data), encoding='utf8'))
            self.send_response(200)
        else:
            response.write(b'not support request')
            self.send_response(404)

        self.end_headers()
        self.wfile.write(response.getvalue())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        input_body = json.loads(
            str(self.rfile.read(content_length), encoding='utf-8'))
        url_result = urlsplit(self.path)
        url_path = url_result.path
        func = self.func_map.get(url_path, None)
        response = BytesIO()
        if func:
            json_data = func(**input_body)
            response.write(bytes(json.dumps(json_data), encoding='utf8'))
            self.send_response(200)
        else:
            response.write(b'not support request')
            self.send_response(404)

        self.end_headers()
        self.wfile.write(response.getvalue())


httpd = HTTPServer(('localhost', 8000), MyHTTPRequestHandler)
httpd.serve_forever()
