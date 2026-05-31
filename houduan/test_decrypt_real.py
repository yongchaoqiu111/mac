import requests
import json
import base64
from file_key_extractor import get_encryption_keys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# 1. 获取钱包列表
print("=" * 60)
print("步骤1: 获取钱包列表")
print("=" * 60)
resp = requests.post('https://api.ai656.top/api/wallet/list')
data = resp.json()

print(f"成功: {data['success']}")
print(f"数量: {len(data['wallets'])}")

first_wallet = data['wallets'][0]
print(f"\n第一个钱包:")
print(f"  ID: {first_wallet['id']}")
print(f"  地址: {first_wallet['address']}")
print(f"  链: {first_wallet['chain']}")
print(f"  encrypted_data长度: {len(first_wallet['encrypted_data'])}")
print(f"  encrypted_data前100字符: {first_wallet['encrypted_data'][:100]}")

# 2. 尝试解密
print("\n" + "=" * 60)
print("步骤2: 尝试解密")
print("=" * 60)

encrypted = first_wallet['encrypted_data']
print(f"原始加密数据: {encrypted}")

try:
    # 检查是否需要填充
    padding_needed = len(encrypted) % 4
    if padding_needed:
        encrypted_padded = encrypted + '=' * (4 - padding_needed)
        print(f"添加填充后: {encrypted_padded[:100]}...")
    else:
        encrypted_padded = encrypted
    
    enc_bytes = base64.b64decode(encrypted_padded)
    print(f"Base64解码成功，字节长度: {len(enc_bytes)}")
    
    client_key, server_key = get_encryption_keys()
    print(f"密钥获取成功")
    
    # 第1次解密：服务器密钥
    nonce = enc_bytes[:12]
    ct = enc_bytes[12:]
    print(f"Nonce长度: {len(nonce)}, Ciphertext长度: {len(ct)}")
    
    aesgcm = AESGCM(server_key)
    client_enc = aesgcm.decrypt(nonce, ct, None).decode('utf-8')
    print(f"第1次解密成功（服务器层）")
    print(f"客户端加密数据长度: {len(client_enc)}")
    
    # 第2次解密：客户端密钥
    client_data = base64.b64decode(client_enc)
    nonce2 = client_data[:12]
    ct2 = client_data[12:]
    
    aesgcm2 = AESGCM(client_key)
    original = aesgcm2.decrypt(nonce2, ct2, None).decode('utf-8')
    print(f"第2次解密成功（客户端层）")
    
    # 解析JSON
    wallet = json.loads(original)
    print(f"\n✅ 解密成功!")
    print(f"  地址: {wallet.get('address', 'N/A')}")
    print(f"  链: {wallet.get('chain', 'N/A')}")
    print(f"  助记词: {wallet.get('mnemonic', 'N/A')[:30]}...")
    print(f"  私钥: {wallet.get('private_key', 'N/A')[:20]}...")
    
except Exception as e:
    print(f"❌ 解密失败: {e}")
    import traceback
    traceback.print_exc()
