import requests
import json

try:
    url = 'https://api.ai656.top/betting/matches/list'
    data = {'game': 'all', 'status': 'upcoming', 'page': 1}
    r = requests.post(url, json=data, timeout=10)
    print(f"状态码: {r.status_code}")
    print(f"响应头: {dict(r.headers)}")
    print(f"响应内容: {r.text[:1000]}")
except Exception as e:
    print(f"错误: {e}")
