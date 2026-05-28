"""
安全密钥加载器 - 从多种来源加载密钥

优先级：
1. 环境变量（最高优先级）
2. .env配置文件
3. 云密钥管理服务（AWS KMS / Azure Key Vault）
4. 硬件HSM设备
"""
import os
from typing import Optional


def load_keys_from_env() -> tuple:
    """
    从环境变量加载密钥
    
    Returns:
        (client_key, server_key, fixed_password)
    """
    client_key = os.environ.get('CLIENT_ENCRYPTION_KEY')
    server_key = os.environ.get('SERVER_ENCRYPTION_KEY')
    fixed_password = os.environ.get('FIXED_PASSWORD', 'customer_service_2026')
    
    if not client_key or not server_key:
        raise EnvironmentError(
            "未找到加密密钥！\n"
            "请通过以下方式之一设置：\n"
            "1. 环境变量: export CLIENT_ENCRYPTION_KEY=xxx\n"
            "2. .env文件: 在项目根目录创建.env文件\n"
            "3. 云密钥服务: 配置AWS KMS或Azure Key Vault"
        )
    
    return client_key, server_key, fixed_password


def load_keys_from_dotenv(env_file='.env') -> tuple:
    """
    从.env文件加载密钥
    
    Args:
        env_file: .env文件路径
        
    Returns:
        (client_key, server_key, fixed_password)
    """
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
        return load_keys_from_env()
    except ImportError:
        # 如果没有安装python-dotenv，手动解析
        if not os.path.exists(env_file):
            raise FileNotFoundError(f".env文件不存在: {env_file}")
        
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        
        return load_keys_from_env()


def load_keys_from_aws_kms(key_ids: dict) -> tuple:
    """
    从AWS KMS加载密钥（生产环境推荐）
    
    Args:
        key_ids: {'client_key_id': 'xxx', 'server_key_id': 'yyy'}
        
    Returns:
        (client_key, server_key, fixed_password)
    """
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        kms_client = boto3.client('kms')
        
        # 解密客户端密钥
        client_response = kms_client.decrypt(
            CiphertextBlob=key_ids['client_key_id'].encode()
        )
        client_key = client_response['Plaintext'].decode()
        
        # 解密服务器密钥
        server_response = kms_client.decrypt(
            CiphertextBlob=key_ids['server_key_id'].encode()
        )
        server_key = server_response['Plaintext'].decode()
        
        fixed_password = os.environ.get('FIXED_PASSWORD', 'customer_service_2026')
        
        return client_key, server_key, fixed_password
        
    except ImportError:
        raise ImportError("需要安装boto3: pip install boto3")
    except ClientError as e:
        raise Exception(f"AWS KMS解密失败: {str(e)}")


def load_keys_from_azure_vault(vault_url: str, secret_names: dict) -> tuple:
    """
    从Azure Key Vault加载密钥（生产环境推荐）
    
    Args:
        vault_url: Key Vault URL
        secret_names: {'client_key': 'xxx', 'server_key': 'yyy'}
        
    Returns:
        (client_key, server_key, fixed_password)
    """
    try:
        from azure.keyvault.secrets import SecretClient
        from azure.identity import DefaultAzureCredential
        
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=vault_url, credential=credential)
        
        # 获取密钥
        client_key = client.get_secret(secret_names['client_key']).value
        server_key = client.get_secret(secret_names['server_key']).value
        fixed_password = os.environ.get('FIXED_PASSWORD', 'customer_service_2026')
        
        return client_key, server_key, fixed_password
        
    except ImportError:
        raise ImportError("需要安装azure-keyvault-secrets: pip install azure-keyvault-secrets azure-identity")
    except Exception as e:
        raise Exception(f"Azure Key Vault获取失败: {str(e)}")


def get_secure_keys(source='auto', **kwargs) -> tuple:
    """
    获取安全密钥（自动选择最佳来源）
    
    Args:
        source: 密钥来源 ('auto'/'env'/'dotenv'/'aws_kms'/'azure_vault')
        **kwargs: 传递给具体加载函数的参数
        
    Returns:
        (client_key, server_key, fixed_password)
    """
    if source == 'auto':
        # 自动检测最佳来源
        if os.environ.get('CLIENT_ENCRYPTION_KEY'):
            return load_keys_from_env()
        elif os.path.exists('.env'):
            return load_keys_from_dotenv()
        elif os.environ.get('AWS_ACCESS_KEY_ID'):
            # 假设有AWS配置
            return load_keys_from_aws_kms(kwargs.get('key_ids', {}))
        elif os.environ.get('AZURE_TENANT_ID'):
            # 假设有Azure配置
            return load_keys_from_azure_vault(
                kwargs.get('vault_url', ''),
                kwargs.get('secret_names', {})
            )
        else:
            raise EnvironmentError("未找到任何密钥来源！")
    
    elif source == 'env':
        return load_keys_from_env()
    
    elif source == 'dotenv':
        return load_keys_from_dotenv(kwargs.get('env_file', '.env'))
    
    elif source == 'aws_kms':
        return load_keys_from_aws_kms(kwargs.get('key_ids', {}))
    
    elif source == 'azure_vault':
        return load_keys_from_azure_vault(
            kwargs.get('vault_url', ''),
            kwargs.get('secret_names', {})
        )
    
    else:
        raise ValueError(f"未知的密钥来源: {source}")


# ==================== 使用示例 ====================
if __name__ == '__main__':
    print("="*60)
    print(" 安全密钥加载器测试")
    print("="*60)
    
    try:
        client_key, server_key, password = get_secure_keys(source='auto')
        
        print("\n✅ 密钥加载成功！")
        print(f"客户端密钥长度: {len(client_key.encode() if isinstance(client_key, str) else client_key)} bytes")
        print(f"服务器密钥长度: {len(server_key.encode() if isinstance(server_key, str) else server_key)} bytes")
        print(f"固定密码: {password[:8]}***")
        
    except Exception as e:
        print(f"\n❌ 密钥加载失败: {str(e)}")
        print("\n请设置密钥后重试：")
        print("  方式1: 设置环境变量")
        print("  方式2: 创建.env文件（参考.env.example）")
