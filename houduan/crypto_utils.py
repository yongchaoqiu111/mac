"""
钱包数据加密解密模块
使用AES-GCM加密算法，确保钱包数据安全
"""
import os
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class WalletCrypto:
    """钱包加密解密工具类"""
    
    # 固定的密钥（实际生产环境应该使用环境变量或密钥管理系统）
    # 32字节 = 256位 AES密钥
    SECRET_KEY = b'MultiChainWallet2026SecureKey32!'
    
    @classmethod
    def encrypt_wallet_data(cls, wallet_data: dict) -> str:
        """
        加密钱包数据
        
        :param wallet_data: 钱包数据字典，包含 private_key, mnemonic, address, chain 等
        :return: Base64编码的加密字符串
        """
        try:
            # 将字典转为JSON字符串
            json_str = json.dumps(wallet_data, ensure_ascii=False)
            json_bytes = json_str.encode('utf-8')
            
            # 生成随机nonce（12字节）
            nonce = os.urandom(12)
            
            # 使用AES-GCM加密
            aesgcm = AESGCM(cls.SECRET_KEY)
            ciphertext = aesgcm.encrypt(nonce, json_bytes, None)
            
            # 将nonce和密文组合并Base64编码
            encrypted_data = nonce + ciphertext
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            raise Exception(f"加密失败: {str(e)}")
    
    @classmethod
    def decrypt_wallet_data(cls, encrypted_str: str) -> dict:
        """
        解密钱包数据
        
        :param encrypted_str: Base64编码的加密字符串
        :return: 钱包数据字典
        """
        try:
            # Base64解码
            encrypted_data = base64.b64decode(encrypted_str)
            
            # 提取nonce（前12字节）和密文
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]
            
            # 使用AES-GCM解密
            aesgcm = AESGCM(cls.SECRET_KEY)
            decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
            
            # 将字节转回JSON字典
            json_str = decrypted_bytes.decode('utf-8')
            return json.loads(json_str)
            
        except Exception as e:
            raise Exception(f"解密失败: {str(e)}")
    
    @classmethod
    def prepare_wallet_for_backup(cls, wallet) -> dict:
        """
        准备钱包数据进行备份
        
        :param wallet: MultiChainWallet实例
        :return: 准备备份的数据字典
        """
        wallet_data = {
            'address': wallet.address,
            'chain': wallet.chain,
            'private_key': wallet.private_key,
        }
        
        # 如果有助记词也包含
        if hasattr(wallet, 'mnemonic') and wallet.mnemonic:
            wallet_data['mnemonic'] = wallet.mnemonic
        
        return wallet_data
    
    @classmethod
    def backup_wallet(cls, wallet) -> str:
        """
        加密并准备钱包数据用于备份
        
        :param wallet: MultiChainWallet实例
        :return: 加密后的字符串
        """
        wallet_data = cls.prepare_wallet_for_backup(wallet)
        return cls.encrypt_wallet_data(wallet_data)
    
    @classmethod
    def restore_wallet(cls, encrypted_str: str):
        """
        解密并恢复钱包数据
        
        :param encrypted_str: 加密的钱包数据
        :return: 钱包数据字典
        """
        return cls.decrypt_wallet_data(encrypted_str)


# 便捷函数
def encrypt_wallet(wallet) -> str:
    """加密钱包（便捷函数）"""
    return WalletCrypto.backup_wallet(wallet)


def decrypt_wallet(encrypted_str: str) -> dict:
    """解密钱包（便捷函数）"""
    return WalletCrypto.restore_wallet(encrypted_str)


if __name__ == '__main__':
    # 测试加密解密
    print("测试加密解密功能...")
    
    # 模拟钱包数据
    test_data = {
        'address': '0x1234567890abcdef1234567890abcdef12345678',
        'chain': 'ETH',
        'private_key': '0xabcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234',
        'mnemonic': 'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about'
    }
    
    # 加密
    encrypted = WalletCrypto.encrypt_wallet_data(test_data)
    print(f"\n原始数据: {test_data}")
    print(f"\n加密后: {encrypted[:50]}...")
    
    # 解密
    decrypted = WalletCrypto.decrypt_wallet_data(encrypted)
    print(f"\n解密后: {decrypted}")
    
    # 验证
    assert test_data == decrypted, "加密解密失败！"
    print("\n✅ 加密解密测试成功！")
