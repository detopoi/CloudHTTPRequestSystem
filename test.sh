#!/bin/bash
ls

# 启动服务器, 使用 & 将其放入后台执行
python python_security_empty.py &

# 等待几秒钟以确保服务器启动
sleep 2

curl -k -X POST http://127.0.0.1:8000/register_user -d '{"name":"test", "username":"test", "password":"test", "email":"test@test", "phone_number": "test", "description":"test"}'

kill $!