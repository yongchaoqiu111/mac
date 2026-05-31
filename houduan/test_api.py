import requests
import json

# 测试1: 获取钱包列表
print("=" * 60)
print("测试1: 获取钱包列表")
print("=" * 60)

list_resp = requests.post('https://api.ai656.top/api/wallet/list')
list_data = list_resp.json()

print(f"成功: {list_data['success']}")
print(f"钱包数量: {len(list_data['wallets'])}")
print(f"\n第一个钱包数据:")
first_wallet = list_data['wallets'][0]
print(json.dumps(first_wallet, indent=2, ensure_ascii=False))

# 测试2: 解密钱包
print("\n" + "=" * 60)
print("测试2: 解密钱包数据")
print("=" * 60)

decrypt_resp = requests.post(
    'https://api.ai656.top/api/admin/decrypt',
    json={'encrypted_data': first_wallet['encrypted_data']},
    headers={'X-Auth-Password': 'admin123'}
)

print(f"状态码: {decrypt_resp.status_code}")
print(f"响应内容: {decrypt_resp.text[:200]}")

try:
    decrypt_data = decrypt_resp.json()
    print(f"成功: {decrypt_data['success']}")
    if decrypt_data['success']:
        wallet_info = json.loads(decrypt_data['decrypted_data'])
        print(f"\n解密后的钱包数据:")
        print(json.dumps(wallet_info, indent=2, ensure_ascii=False))
    else:
        print(f"错误: {decrypt_data['message']}")
except Exception as e:
    print(f"解析失败: {e}")
    print(f"原始响应: {decrypt_resp.text}")
