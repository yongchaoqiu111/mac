"""
解密核心模块 - 密钥与算法分离架构

使用方式：
1. 将 KEY_N 存储在安全位置（环境变量/配置文件/密钥管理服务）
2. 算法代码可以公开部署
3. 运行时动态传入密钥参数
"""
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def decrypt_double(encrypted_str: str, key_n: bytes) -> str:
    """
    双重解密核心算法
    
    Args:
        encrypted_str: Base64编码的双重加密数据
        key_n: 完整密钥参数（32字节），从安全位置获取
        
    Returns:
        原始明文数据
        
    Raises:
        Exception: 解密失败时抛出异常
    """
    if len(key_n) != 32:
        raise ValueError(f"密钥长度错误：需要32字节，实际{len(key_n)}字节")
    
    try:
        # 第1层解密：用服务器密钥（从key_n派生或独立存储）
        SERVER_KEY = key_n[:32]  # 示例：使用前32字节作为服务器密钥
        
        encrypted_data = base64.b64decode(encrypted_str)
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        aesgcm = AESGCM(SERVER_KEY)
        client_encrypted = aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
        
        # 第2层解密：用客户端密钥（从key_n派生或独立存储）
        CLIENT_KEY = key_n[32:64] if len(key_n) >= 64 else key_n  # 示例：后32字节或复用
        
        client_data = base64.b64decode(client_encrypted)
        nonce2 = client_data[:12]
        ciphertext2 = client_data[12:]
        aesgcm2 = AESGCM(CLIENT_KEY)
        original_data = aesgcm2.decrypt(nonce2, ciphertext2, None).decode('utf-8')
        
        return original_data
        
    except Exception as e:
        raise Exception(f"解密失败: {str(e)}")


# ==================== 使用示例 ====================
if __name__ == '__main__':
    # 从安全位置获取密钥（环境变量/配置文件/密钥服务）
    import os
    
    # 方式1：从环境变量读取
    KEY_N = os.environ.get('WALLET_DECRYPT_KEY_N', '').encode('utf-8')
    
    if not KEY_N:
        print("❌ 错误：未设置 WALLET_DECRYPT_KEY_N 环境变量")
        print("请设置：export WALLET_DECRYPT_KEY_N='你的完整密钥'")
    else:
        print("✅ 解密核心模块加载成功")
        print(f"密钥长度: {len(KEY_N)} bytes")
        print("\n使用方法:")
        print("  from decrypt_core_v2 import decrypt_double")
        print("  result = decrypt_double(encrypted_data, KEY_N)")
