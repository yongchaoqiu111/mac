"""
独立解密工具 - 可部署到其他服务器
通过密码验证 → 获取加密数据 → 本地双重解密
"""
import requests
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class WalletDecryptor:
    """钱包解密器"""
    
    # 双重加密密钥（与服务器一致）
    CLIENT_ENCRYPTION_KEY = b'ClientWallet2026SecureKey32B!!!!'
    SERVER_ENCRYPTION_KEY = b'ServerWallet2026SecureKey32B!!!!'
    
    def __init__(self, server_api, password):
        """
        初始化解密器
        
        Args:
            server_api: 服务器API地址（如 http://api.ai656.top）
            password: 时效密码
        """
        self.server_api = server_api
        self.password = password
        self.authorized = False
    
    def verify_password(self):
        """
        验证密码是否有效
        
        Returns:
            {'success': True/False, 'message': '提示信息'}
        """
        try:
            response = requests.post(
                f'{self.server_api}/api/admin/verify_password',
                json={'password': self.password},
                timeout=10
            )
            
            result = response.json()
            if result.get('success'):
                self.authorized = True
                return {'success': True, 'message': '验证成功'}
            else:
                return {'success': False, 'message': result.get('message', '密码错误')}
        
        except Exception as e:
            return {'success': False, 'message': f'连接失败: {str(e)}'}
    
    def get_all_backups(self):
        """
        获取所有备份数据（加密状态）
        
        Returns:
            {'success': True/False, 'wallets': [...], 'message': '...'}
        """
        if not self.authorized:
            return {'success': False, 'message': '请先验证密码'}
        
        try:
            response = requests.get(
                f'{self.server_api}/api/admin/list_all',
                headers={'X-Auth-Password': self.password},
                timeout=10
            )
            
            result = response.json()
            if result.get('success'):
                return {
                    'success': True,
                    'wallets': result.get('wallets', []),
                    'count': result.get('count', 0)
                }
            else:
                return {'success': False, 'message': result.get('message')}
        
        except Exception as e:
            return {'success': False, 'message': f'获取失败: {str(e)}'}
    
    def decrypt_double(self, encrypted_str: str) -> str:
        """
        双重解密（本地执行）
        第1次：用服务器密钥解密
        第2次：用客户端密钥解密
        
        Args:
            encrypted_str: Base64编码的双重加密数据
            
        Returns:
            解密后的原始数据
        """
        try:
            # 第1次解密：去掉服务器加密层
            encrypted_data = base64.b64decode(encrypted_str)
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]
            aesgcm = AESGCM(self.SERVER_ENCRYPTION_KEY)
            client_encrypted = aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
            
            # 第2次解密：去掉客户端加密层
            client_data = base64.b64decode(client_encrypted)
            nonce2 = client_data[:12]
            ciphertext2 = client_data[12:]
            aesgcm2 = AESGCM(self.CLIENT_ENCRYPTION_KEY)
            original_data = aesgcm2.decrypt(nonce2, ciphertext2, None).decode('utf-8')
            
            return original_data
        
        except Exception as e:
            return f"解密失败: {str(e)}"
    
    def decrypt_wallet_address(self, wallet_index=0):
        """
        解密指定钱包的地址
        
        Args:
            wallet_index: 钱包索引（从0开始）
            
        Returns:
            {'success': True/False, 'address': '解密后的地址', 'chain': '链', ...}
        """
        if not self.authorized:
            return {'success': False, 'message': '请先验证密码'}
        
        # 获取所有备份
        backups = self.get_all_backups()
        if not backups['success']:
            return backups
        
        wallets = backups['wallets']
        if wallet_index >= len(wallets):
            return {'success': False, 'message': f'索引超出范围，共有{len(wallets)}个钱包'}
        
        wallet = wallets[wallet_index]
        
        # 本地解密地址
        decrypted_address = self.decrypt_double(wallet['address'])
        decrypted_chain = self.decrypt_double(wallet['chain'])
        decrypted_time = self.decrypt_double(wallet['backup_time'])
        
        return {
            'success': True,
            'id': wallet['id'],
            'backup_id': wallet['backup_id'],
            'address': decrypted_address,
            'chain': decrypted_chain,
            'backup_time': decrypted_time
        }
    
    def decrypt_all_addresses(self):
        """
        解密所有钱包地址
        
        Returns:
            {'success': True/False, 'wallets': [...], 'message': '...'}
        """
        if not self.authorized:
            return {'success': False, 'message': '请先验证密码'}
        
        # 获取所有备份
        backups = self.get_all_backups()
        if not backups['success']:
            return backups
        
        # 本地解密所有地址
        decrypted_wallets = []
        for wallet in backups['wallets']:
            try:
                decrypted_wallet = {
                    'id': wallet['id'],
                    'backup_id': wallet['backup_id'],
                    'address': self.decrypt_double(wallet['address']),
                    'chain': self.decrypt_double(wallet['chain']),
                    'backup_time': self.decrypt_double(wallet['backup_time']),
                }
                decrypted_wallets.append(decrypted_wallet)
            except Exception as e:
                decrypted_wallets.append({
                    'id': wallet['id'],
                    'backup_id': wallet['backup_id'],
                    'address': f'解密失败: {str(e)}',
                    'chain': '未知',
                    'backup_time': '未知'
                })
        
        return {
            'success': True,
            'count': len(decrypted_wallets),
            'wallets': decrypted_wallets
        }


def main():
    """测试示例"""
    print("="*60)
    print(" 独立解密工具测试")
    print("="*60)
    
    # 配置
    SERVER_API = 'http://api.ai656.top'
    PASSWORD = input("\n请输入时效密码: ").strip()
    
    # 初始化解密器
    decryptor = WalletDecryptor(SERVER_API, PASSWORD)
    
    # 1. 验证密码
    print("\n【步骤1】验证密码...")
    verify_result = decryptor.verify_password()
    print(f"结果: {verify_result}")
    
    if not verify_result['success']:
        print("\n 密码验证失败，退出！")
        return
    
    # 2. 获取所有备份
    print("\n【步骤2】获取所有备份...")
    backups = decryptor.get_all_backups()
    print(f"共找到 {backups.get('count', 0)} 个备份")
    
    if not backups['success'] or backups['count'] == 0:
        print("\n❌ 没有备份数据，退出！")
        return
    
    # 3. 解密所有地址
    print("\n【步骤3】本地解密所有地址...")
    decrypted = decryptor.decrypt_all_addresses()
    
    if decrypted['success']:
        print(f"\n✅ 成功解密 {decrypted['count']} 个钱包：\n")
        print(f"{'ID':<5} {'备份ID':<25} {'钱包地址':<45} {'链':<12}")
        print("-" * 90)
        
        for wallet in decrypted['wallets']:
            print(f"{wallet['id']:<5} {wallet['backup_id']:<25} {wallet['address']:<45} {wallet['chain']:<12}")
    
    print("\n" + "="*60)
    print("✅ 解密完成！")
    print("="*60)


if __name__ == '__main__':
    main()
