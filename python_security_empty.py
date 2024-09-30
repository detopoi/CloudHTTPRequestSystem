import json
import logging
import random
import os
import subprocess
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
    log_file = 'operation.log'
    today_database = {}
    today_ids = {}

    def __init__(self):
        MaintainBiz.get_today_user_data()

    @staticmethod
    def ensure_database_folder():
        """ Check the path of the database"""
        if not os.path.exists(MaintainBiz.database_folder):
            os.makedirs(MaintainBiz.database_folder)

    @staticmethod
    def ensure_script_folder():
        """ Check the path of the script"""
        if not os.path.exists(MaintainBiz.script_directory):
            os.makedirs(MaintainBiz.script_directory)

    @staticmethod
    def get_today_user_data():
        """ Extract all registered users of today"""
        today_date = datetime.now().strftime("%Y%m%d")
        file_path = os.path.join(MaintainBiz.database_folder, f"{today_date}.json")
        if not os.path.exists(file_path):
            MaintainBiz.today_ids, MaintainBiz.today_database = set(), set()
        with open(file_path, 'r') as user_file:
            data = json.load(user_file)
            MaintainBiz.today_ids, MaintainBiz.today_database = \
                set(data.get('user_ids', [])), set(data.get('usernames', []))

    @staticmethod
    def save_today_user_data(user_ids, usernames):
        """ Save the data of all users today"""
        today_date = datetime.now().strftime("%Y%m%d")
        file_path = os.path.join(MaintainBiz.database_folder, f"{today_date}.json")
        data = {'user_ids': list(user_ids), 'usernames': list(usernames)}
        with open(file_path, 'w') as user_file:
            json.dump(data, user_file, indent=4, ensure_ascii=False)

    @staticmethod
    def generate_user_id():
        """ Generate a new id for user

        @return: new id
        """
        date_str = datetime.now().strftime("%Y%m%d")
        random_num = random.randint(0, 99999999)
        zeros = 8-len(str(random_num))
        if zeros > 0:
            return date_str + "0"*zeros + str(random_num)
        return f"{date_str}{random_num}"

    @staticmethod
    def is_username_taken(username):
        """ Check if the username has been created

        @return: (if the username has been taken)
        """
        MaintainBiz.get_today_user_data()
        return username in MaintainBiz.today_database

    @staticmethod
    def register_user(**user_info):
        """ Automatically register a new account for user

        @param user_info
        @return: (if the registration is successful)
        """
        name, username, password, email, phone_number, description = (
            user_info.get('name'), user_info.get("username"), user_info.get("password"),
            user_info.get("email"), user_info.get("phone_number"), user_info.get("description")
        )

        if not all([name, username, password, email, phone_number]):
            return {'status': 'fail', 'message': 'Please fill all the necessary information'}

        if MaintainBiz.is_username_taken(username):
            return {'status': 'fail', 'message': 'Username has been used'}

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

        file_path = f"./user_data/USER-{user_id}.json"
        try:
            with open(file_path, 'w') as user_file:
                json.dump(user_data, user_file, indent=4, ensure_ascii=False)
        except Exception as e:
            return {'status': 'fail', 'message': str(e)}

        # Update the user id and the set for all users
        MaintainBiz.get_today_user_data()
        user_ids, usernames = MaintainBiz.today_ids, MaintainBiz.today_database
        user_ids.add(user_id)
        usernames.add(username)
        MaintainBiz.save_today_user_data(user_ids, usernames)

        return {'status': 'success', 'message': "Successfully create a account with: "+str(user_data)}

    @staticmethod
    def query_user_info(user_id):
        """ 查询用户信息

        @param user_id 用户ID
        @return 用户信息详情
        """
        user_id = str(user_id)
        if len(user_id) != 8:
            return {'status': 'fail', 'message': f"Wrong id format, expect 8 digits but got {len(user_id)}"}
        for user_data in os.listdir('./user_data'):
            data_id = user_data[13:21]
            if user_id == data_id:
                file_path = os.path.join(MaintainBiz.user_folder, user_data)
                try:
                    with open(file_path, 'r') as user_file:
                        data = json.load(user_file)
                except Exception as e:
                    return {'status': 'fail', 'message': "Error: "+str(e)}
                return {'status': 'success', 'message': data}
        return {'status': 'fail', 'message': "User not found"}

    @staticmethod
    def upload_script(**kwargs):
        """ 上传运维script脚本, 将zip解压后将脚本归档到到目录下。

        @param kwargs  {'script_name':xxxx, 'user_id': id}
        @return 成功与否
        """

        script_name = kwargs.get('script_name')
        args = kwargs.get('args')
        user_id = kwargs.get('user_id')

        if MaintainBiz.query_user_info(user_id)["status"] == "fail":
            return {'status': 'fail', 'message': 'User not found'}

        zip_file_path = f"./uploads/{script_name}"
        if not os.path.exists(zip_file_path):
            return {'status': 'fail', 'message': 'zip file not found'}

        MaintainBiz.ensure_script_folder()
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(MaintainBiz.script_directory)
        except Exception as e:
            return {'status': 'fail', 'message': str(e)}

        return {'status': 'success',
                'message': str({
                    'script_name': script_name,
                    'args': args,
                    'user_id': user_id})
                }

    @staticmethod
    def log_operation(user_id, script_path, result):
        """ Record the operated information """
        with open(MaintainBiz.log_file, 'a') as log_file:
            log_file.write(f"{datetime.now()} - User ID: {user_id}, Script: {script_path}, Result: {result}\n")

    @staticmethod
    def process_maintain_script(**kwargs):
        """ 执行运维任务

        @param kwargs 待执行的运维脚本, 脚本参数, 执行用户 {'script_name': xxxx, 'args': ['yyy', 'zzz'], 'user_id': id}
        @return 成功与否 {'script_name':xxxx, 'args': ['yyy', 'zzz'], 'user_id': id}
        """
        script_name = kwargs.get('script_name')
        user_id = kwargs.get('user_id')
        args = kwargs.get('args')

        if not os.path.exists(f"scripts/{script_name}"):
            return {'status': 'fail', 'message': 'Script file not found'}

        try:
            command = [script_name] + args
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout
            error = result.stderr
            MaintainBiz.log_operation(user_id, script_name, f"Executed successfully. Output: {output}")
            return {"status": 'success', "message": output}
        except subprocess.CalledProcessError as e:
            MaintainBiz.log_operation(user_id, script_name, f"Execution failed. Error: {e.stderr}")
            return {'status': 'fail', 'message': e.stderr}


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



