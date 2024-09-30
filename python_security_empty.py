import json
import logging
import random
import os
import zipfile
from datetime import datetime
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
    database_folder = "database_user"
    user_folder = "user_data"
    script_directory = "scripts"
    today_database = {}
    today_ids = {}

    def __init__(self):
        MaintainBiz.get_today_user_data()

    @staticmethod
    def ensure_database_folder():
        """ 检查数据库路径
        """
        if not os.path.exists(MaintainBiz.database_folder):
            os.makedirs(MaintainBiz.database_folder)

    @staticmethod
    def ensure_script_folder():
        """ 检查脚本路径
        """
        if not os.path.exists(MaintainBiz.script_directory):
            os.makedirs(MaintainBiz.script_directory)

    @staticmethod
    def get_today_user_data():
        """ 读取今日注册用户
        """
        today_date = datetime.now().strftime("%Y%m%d")
        file_path = os.path.join(MaintainBiz.database_folder, f"{today_date}.json")

        if not os.path.exists(file_path):
            MaintainBiz.today_ids, MaintainBiz.today_database = set(), set()
            # return set(), set()  # 返回空集合，表示没有用户

        with open(file_path, 'r') as user_file:
            data = json.load(user_file)
            MaintainBiz.today_ids, MaintainBiz.today_database = \
                set(data.get('user_ids', [])), set(data.get('usernames', []))
            # return set(data.get('user_ids', [])), set(data.get('usernames', []))

    @staticmethod
    def save_today_user_data(user_ids, usernames):
        """ 保存今日总用户
        """
        today_date = datetime.now().strftime("%Y%m%d")
        file_path = os.path.join(MaintainBiz.database_folder, f"{today_date}.json")

        data = {'user_ids': list(user_ids), 'usernames': list(usernames)}

        with open(file_path, 'w') as user_file:
            json.dump(data, user_file, indent=4, ensure_ascii=False)

    @staticmethod
    def generate_user_id():
        """ 生成新用户id
        """
        date_str = datetime.now().strftime("%Y%m%d")
        random_num = random.randint(10000000, 99999999)
        return f"{date_str}{random_num}"

    @staticmethod
    def is_username_taken(username):
        """ 用户名是否已存在
        """
        MaintainBiz.get_today_user_data()
        return username in MaintainBiz.today_database
        # _, usernames = MaintainBiz.today_ids, MaintainBiz.today_database
        # return username in usernames

    @staticmethod
    def register_user(**user_info):
        """ 自助注册新用户

        @param user_info 用户信息
        @return 注册成功与否
        """
        name, username, password, email, phone_number, description = (
            user_info.get('name'), user_info.get("username"), user_info.get("password"),
            user_info.get("email"), user_info.get("phone_number"), user_info.get("description")
        )

        if not all([name, username, password, email, phone_number]):
            return {'status': 'fail', 'message': '缺少必要信息'}

        # 检查用户名唯一性
        if MaintainBiz.is_username_taken(username):
            return {'status': 'fail', 'message': '用户名已被使用'}

        user_id = MaintainBiz.generate_user_id()
        user_data = {
            "name": name,
            "user_id": user_id,
            "username": username,
            "password": password,
            "email": email,
            "phone_number": phone_number,
            "description": description
        }

        # 保存用户信息到文件
        file_path = f"./user_data/USER-{user_id}.json"
        try:
            with open(file_path, 'w') as user_file:
                json.dump(user_data, user_file, indent=4, ensure_ascii=False)
        except Exception as e:
            return {'status': 'fail', 'message': str(e)}

        # 更新用户ID和用户名集合
        MaintainBiz.get_today_user_data()
        user_ids, usernames = MaintainBiz.today_ids, MaintainBiz.today_database
        user_ids.add(user_id)
        usernames.add(username)
        MaintainBiz.save_today_user_data(user_ids, usernames)

        return {'status': 'success', 'message': "创建成功, 账号信息: "+str(user_data)}

    @staticmethod
    def query_user_info(user_id):
        """ 查询用户信息

        @param user_id 用户ID
        @return 用户信息详情
        """
        for user_data in os.listdir('./user_data'):
            data_id = user_data[13:21]
            if str(user_id) == data_id:
                file_path = os.path.join(MaintainBiz.user_folder, user_data)
                try:
                    with open(file_path, 'r') as user_file:
                        data = json.load(user_file)
                except Exception as e:
                    return {"Error": str(e)}
                return data
        return {}

    @staticmethod
    def process_maintain_script(**kwargs):
        """ 执行运维任务
        运维人员会上传script脚本用于用于自动化运维，假设上传的script脚本已经压缩为zip格式并保存到服务器上，该操作只需要将zip解压后将脚本归档到到目录下。

        @param kwargs 待执行的运维脚本，脚本参数, 执行用户 {'script_name':xxxx, 'args': ['yyy', 'zzz'], 'user_id': id}
        @return 成功与否 {'script_name':xxxx, 'args': ['yyy', 'zzz'], 'user_id': id}
        """


        # TODO
        return {'status': 'success', 'message': 'Yeah!'}

    @staticmethod
    def upload_script(**kwargs):
        """ 上传运维script脚本

        @param kwargs  {'script_name':xxxx, 'user_id': id}
        @return 成功与否
        """

        # TODO
        return {'status': 'success', 'message': 'Yeah!'}


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


if __name__ == '__main__':
    httpd = HTTPServer(('localhost', 8000), MyHTTPRequestHandler)
    httpd.serve_forever()



