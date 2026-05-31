import requests

try:
    r = requests.post('https://api.ai656.top/betting/matches/list', json={'game': 'all'}, timeout=10)
    print(f"状态码: {r.status_code}")
    print(f"响应: {r.text[:1000]}")
except Exception as e:
    print(f"错误: {e}")
