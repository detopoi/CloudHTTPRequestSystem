import json
import logging
import random
import requests
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from io import BytesIO
from urllib.parse import parse_qs
from urllib.parse import urlsplit


if __name__ == '__main__':
    while True:
        print("-----------------------------------------------------------------------------------")
        print("输入新注册:用户名")
        username = input()
        url = "http://localhost:8000/register_user"
        data = {
            "name": "XiaoMing",
            "username": username,
            "password": "securepassword",
            "email": "xiaoming@example.com",
            "phone_number": "123456789",
            "description": "新用户"
        }
        response = requests.post(url, json=data)
        print(response.json())

        print("-----------------------------------------------------------------------------------")
        print("输入要查询的用户id")  # 51367338
        userid = input()
        url = "http://localhost:8000/query_user_info"
        response = requests.post(url, json={"user_id": userid})
        print(response.json())

        print("-----------------------------------------------------------------------------------")
        print("是否尝试解压(y/s):")
        is_unzip = input().lower()
        if is_unzip == "y":
            print("输入解压用户id:")
            userid = input()
            url = "http://localhost:8000/upload_script"
            response = requests.post(url, json={"script_name": "test.zip", "user_id": userid})
            print(response.json())

        print("-----------------------------------------------------------------------------------")
        print("输入测试用户id")  # 51367338
        user_id = input()
        url = "http://localhost:8000/process_maintain_script"
        data = {
            "script_name": "test1.sh",
            "args": {"user_id": user_id, "script_name": "test1.sh"},
            "user_id": user_id
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Response JSON:", response.json())
        else:
            print("Error:", response.status_code, response.text)
