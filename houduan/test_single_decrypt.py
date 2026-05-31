import requests
import json
import base64
from file_key_extractor import get_encryption_keys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# 获取钱包列表
resp = requests.post('https://api.ai656.top/api/wallet/list')
data = resp.json()

first_wallet = data['wallets'][0]
encrypted = first_wallet['encrypted_data']

print(f"地址: {first_wallet['address']}")
print(f"加密数据长度: {len(encrypted)}")
print(f"加密数据: {encrypted}")

client_key, server_key = get_encryption_keys()

# 尝试1: 只用服务器密钥解密（单层）
print("\n" + "="*60)
print("尝试1: 只用服务器密钥解密（单层）")
print("="*60)
try:
    enc_bytes = base64.b64decode(encrypted)
    nonce = enc_bytes[:12]
    ct = enc_bytes[12:]
    aesgcm = AESGCM(server_key)
    decrypted = aesgcm.decrypt(nonce, ct, None).decode('utf-8')
    
    print(f"✅ 单层解密成功!")
    print(f"解密结果: {decrypted[:200]}")
    
    # 尝试解析JSON
    try:
        wallet_info = json.loads(decrypted)
        print(f"\n✅ 可以直接解析为JSON!")
        print(f"地址: {wallet_info.get('address')}")
        print(f"链: {wallet_info.get('chain')}")
    except:
        print(f"\n❌ 不是JSON格式")
        
except Exception as e:
    print(f"❌ 单层解密失败: {e}")
