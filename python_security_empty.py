import json
import logging
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


class MaintainBiz():

    @staticmethod
    def register_user(**user_info):
        """ 自助注册新用户

        @param user_info 用户信息
        @return 注册成功与否
        """

        # TODO
        return {'status': 'success', 'message':''}

    @staticmethod
    def query_user_info(user_id):
        """ 查询用户信息

        @param user_id 用户ID
        @return 用户信息详情
        """

        # TODO
        return {}

    @staticmethod
    def process_maintain_script(**kwargs):
        """ 执行运维任务

        @param kwargs 待执行的运维脚本，脚本参数, 执行用户 {'script_name':xxxx, 'args': ['yyy', 'zzz'], 'user_id': id}
        @return 成功与否 {'script_name':xxxx, 'args': ['yyy', 'zzz'], 'user_id': id}
        """
        # TODO
        return {'status': 'success', 'message':''}

    @staticmethod
    def upload_script(**kwargs):
        """ 上传运维script脚本

        @param kwargs  {'script_name':xxxx, 'user_id': id}
        @return 成功与否
        """

        # TODO
        return {'status': 'success', 'message':''}


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    func_map = {'/register_user': MaintainBiz.register_user,
                '/query_user_info': MaintainBiz.query_user_info,
                '/process_maintain_script': MaintainBiz.process_maintain_script,
                '/upload_script': MaintainBiz.upload_script}

    def do_GET(self):
        url_result = urlsplit(self.path)
        url_path = url_result.path
        query_info_dict = parse_qs(url_result.query)
        user_id = query_info_dict.get('user_id')
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
