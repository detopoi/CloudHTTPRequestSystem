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

        print("输入要查询的用户id")  # 51367338
        userid = input()
        url = "http://localhost:8000/query_user_info"
        response = requests.post(url, json={"user_id": userid})
        print(response.json())
