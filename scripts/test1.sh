#!/bin/bash

curl -k -X POST http://127.0.0.1:8000/register_user -d '{"name":"test", "username":"xiaoming", "password":"test", "email":"test@test", "phone_number": "test", "description":"test"}'
curl -k -X POST http://127.0.0.1:8000/register_user -d '{"name":"test", "username":"dwadesfgs", "password":"123456t", "email":"hw123@gmail.com", "phone_number": "+44 7031253241", "description":"test"}'

curl -k -X GET http://127.0.0.1:8000/query_user_info?user_id="12345678"
curl -k -X GET http://127.0.0.1:8000/query_user_info?user_id="51367338"

curl -k -X POST http://127.0.0.1:8000/upload_script -d '{"script_name":"test.zip", "user_id": "id"}'
curl -k -X POST http://127.0.0.1:8000/upload_script -d '{"script_name":"test.zip", "user_id": "51367338"}'

curl -X POST http://127.0.0.1:8000/process_maintain_script -d '{"script_path": "scripts/test.sh", "args": ["test"], "user_id": "id"}'
curl -X POST http://127.0.0.1:8000/process_maintain_script -d '{"script_path": "scripts/test.sh", "args": ["test"], "user_id": "51367338"}'