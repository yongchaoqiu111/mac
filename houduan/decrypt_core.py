"""
解密核心模块 - 仅包含关键算法和参数
可独立部署到任何Python环境

安全说明：
- 密钥必须从环境变量或配置文件加载
- 严禁在代码中硬编码密钥
"""
import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def get_encryption_keys():
    """
    从多种来源获取加密密钥（优先级从高到低）
    
    1. 本地缓存文件（key_manager_client下载）
    2. 本地ICO/PNG文件名（隐写术）
    3. GitHub图片文件名
    4. 环境变量
    5. .env配置文件
    
    Returns:
        (client_key_bytes, server_key_bytes)
    """
    # 第1优先：尝试从缓存加载
    try:
        from key_manager_client import KeyManagerClient
        client = KeyManagerClient()
        cached_keys = client._load_cached_keys()
        if cached_keys:
            return cached_keys['client_key'], cached_keys['server_key']
    except:
        pass
    
    # 第2优先：从本地ICO/PNG文件名提取
    try:
        from local_file_key_extractor import get_keys as get_local_keys
        
        client_key_str, server_key_str = get_local_keys()
        
        if client_key_str and server_key_str:
            client_key = client_key_str.encode('utf-8')
            server_key = server_key_str.encode('utf-8')
            
            if len(client_key) == 32 and len(server_key) == 32:
                print("✅ 从本地文件文件名加载密钥")
                return client_key, server_key
    except:
        pass
    
    # 第3优先：从GitHub图片文件名提取
    try:
        from github_image_key_extractor import get_keys_from_github
        
        # 从环境变量读取GitHub配置
        repo_owner = os.environ.get('GITHUB_KEY_REPO_OWNER', 'your_username')
        repo_name = os.environ.get('GITHUB_KEY_REPO_NAME', 'secret-keys')
        
        client_key_str, server_key_str = get_keys_from_github(repo_owner, repo_name)
        
        if client_key_str and server_key_str:
            client_key = client_key_str.encode('utf-8')
            server_key = server_key_str.encode('utf-8')
            
            if len(client_key) == 32 and len(server_key) == 32:
                print("✅ 从GitHub图片文件名加载密钥")
                return client_key, server_key
    except:
        pass
    
    # 第4优先：环境变量
    client_key_str = os.environ.get('CLIENT_ENCRYPTION_KEY')
    server_key_str = os.environ.get('SERVER_ENCRYPTION_KEY')
    
    if client_key_str and server_key_str:
        # 如果是hex编码（64字符），转换为bytes
        if len(client_key_str) == 64:
            client_key = bytes.fromhex(client_key_str)
            server_key = bytes.fromhex(server_key_str)
        else:
            client_key = client_key_str.encode('utf-8')
            server_key = server_key_str.encode('utf-8')
        
        # 验证密钥长度
        if len(client_key) == 32 and len(server_key) == 32:
            return client_key, server_key
    
    # 第5优先：.env文件
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        client_key_str = os.environ.get('CLIENT_ENCRYPTION_KEY')
        server_key_str = os.environ.get('SERVER_ENCRYPTION_KEY')
        
        if client_key_str and server_key_str:
            if len(client_key_str) == 64:
                client_key = bytes.fromhex(client_key_str)
                server_key = bytes.fromhex(server_key_str)
            else:
                client_key = client_key_str.encode('utf-8')
                server_key = server_key_str.encode('utf-8')
            
            if len(client_key) == 32 and len(server_key) == 32:
                return client_key, server_key
    except:
        pass
    
    raise EnvironmentError(
        "未找到加密密钥！\n"
        "请通过以下方式之一提供密钥：\n"
        "1. 使用KeyManagerClient登录并下载密钥（推荐）\n"
        "2. 创建ICO/PNG文件，文件名为密钥（参考local_file_key_extractor.py）\n"
        "3. 在GitHub创建公开仓库，上传空图片，文件名为密钥\n"
        "4. 设置环境变量: export CLIENT_ENCRYPTION_KEY=xxx\n"
        "5. 创建.env文件（参考.env.example）"
    )


def decrypt_double(encrypted_str: str) -> str:
    """
    双重解密核心算法
    
    Args:
        encrypted_str: Base64编码的双重加密数据
        
    Returns:
        原始明文数据
        
    Raises:
        Exception: 解密失败时抛出异常
    """
    try:
        # 动态获取密钥（从环境变量）
        CLIENT_KEY, SERVER_KEY = get_encryption_keys()
        
        # 第1层解密：用服务器密钥
        encrypted_data = base64.b64decode(encrypted_str)
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        aesgcm = AESGCM(SERVER_KEY)
        client_encrypted = aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
        
        # 第2层解密：用客户端密钥
        client_data = base64.b64decode(client_encrypted)
        nonce2 = client_data[:12]
        ciphertext2 = client_data[12:]
        aesgcm2 = AESGCM(CLIENT_KEY)
        original_data = aesgcm2.decrypt(nonce2, ciphertext2, None).decode('utf-8')
        
        return original_data
        
    except base64.binascii.Error:
        raise Exception("数据格式错误：非Base64编码")
    except ValueError as e:
        if "MAC check failed" in str(e):
            raise Exception("密钥错误或数据被篡改")
        raise
    except Exception as e:
        raise Exception(f"解密失败: {type(e).__name__} - {str(e)}")


# ==================== 使用示例 ====================
if __name__ == '__main__':
    print("✅ 解密核心模块加载成功")
    print("\n⚠️  使用前请设置环境变量：")
    print("   Linux/Mac: export CLIENT_ENCRYPTION_KEY='xxx' && export SERVER_ENCRYPTION_KEY='yyy'")
    print("   Windows: set CLIENT_ENCRYPTION_KEY=xxx && set SERVER_ENCRYPTION_KEY=yyy")
    print("\n使用方法:")
    print("  from decrypt_core import decrypt_double")
    print("  result = decrypt_double(encrypted_data)")
