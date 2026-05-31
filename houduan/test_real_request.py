import requests
import json

print("=" * 80)
print("真实POST请求测试 - /api/wallet/list")
print("=" * 80)

# 发送POST请求
resp = requests.post('https://api.ai656.top/api/wallet/list')

print(f"\n状态码: {resp.status_code}")
print(f"响应头: {dict(resp.headers)}")
print(f"\n完整JSON响应:")
print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
