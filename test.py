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

url = "http://localhost:8000/register_user"
data = {
    "name": "XiaoMing",
    "username": "xiaoming",
    "password": "securepassword",
    "email": "xiaoming@example.com",
    "phone_number": "123456789",
    "description": "新用户"
}


if __name__ == '__main__':
    response = requests.post(url, json=data)
    print(response.json())

