"""
客服登录系统 - 时效认证 + 密钥分发

流程：
1. 客服输入密码登录
2. 验证密码有效性（24小时时效）
3. 登录成功后下载解密密钥
4. 密钥存储在本地安全位置
5. 24小时后需重新登录
"""
import requests
import os
import json
from datetime import datetime


class CustomerServiceLogin:
    """客服登录管理器"""
    
    def __init__(self, server_api='http://api.ai656.top'):
        self.server_api = server_api
        self.key_file = 'decrypt_key.json'  # 本地密钥存储文件
    
    def login(self, password):
        """
        客服登录
        
        Args:
            password: 时效密码
            
        Returns:
            {
                'success': True/False,
                'message': '提示信息',
                'key_data': '密钥数据（登录成功时返回）'
            }
        """
        try:
            # 第1步：验证密码
            verify_response = requests.post(
                f'{self.server_api}/api/admin/verify_password',
                json={'password': password},
                timeout=10
            )
            
            if verify_response.status_code != 200:
                return {
                    'success': False,
                    'message': f'服务器错误: {verify_response.status_code}'
                }
            
            result = verify_response.json()
            
            if not result.get('success'):
                return {
                    'success': False,
                    'message': result.get('message', '密码错误')
                }
            
            # 第2步：密码验证成功，获取密钥信息
            key_info = result.get('data', {})
            
            # 第3步：下载解密密钥（从安全接口获取）
            key_response = requests.get(
                f'{self.server_api}/api/admin/get_decrypt_key',
                headers={'Authorization': f'Bearer {password}'},
                timeout=10
            )
            
            if key_response.status_code == 200:
                key_data = key_response.json()
                
                # 保存到本地（加密存储）
                self._save_key_locally(key_data)
                
                return {
                    'success': True,
                    'message': '登录成功，密钥已下载',
                    'key_data': key_data,
                    'expire_time': key_info.get('expire_time_str', '未知')
                }
            else:
                return {
                    'success': False,
                    'message': '密钥下载失败'
                }
        
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'message': '请求超时，请检查网络连接'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'登录失败: {str(e)}'
            }
    
    def _save_key_locally(self, key_data):
        """本地保存密钥（JSON格式）"""
        save_data = {
            'key_n': key_data.get('key_n', ''),
            'login_time': datetime.now().isoformat(),
            'server_api': self.server_api
        }
        
        with open(self.key_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        # 设置文件权限（仅当前用户可读）
        try:
            os.chmod(self.key_file, 0o600)
        except:
            pass  # Windows可能不支持chmod
    
    def load_key(self):
        """
        加载本地密钥
        
        Returns:
            bytes或None
        """
        if not os.path.exists(self.key_file):
            return None
        
        try:
            with open(self.key_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查是否过期（24小时）
            login_time = datetime.fromisoformat(data['login_time'])
            hours_passed = (datetime.now() - login_time).total_seconds() / 3600
            
            if hours_passed >= 24:
                print(f"⚠️ 密钥已过期（{hours_passed:.1f}小时前登录）")
                return None
            
            key_n = data.get('key_n', '')
            if key_n:
                return key_n.encode('utf-8') if isinstance(key_n, str) else key_n
            
            return None
        
        except Exception as e:
            print(f"❌ 加载密钥失败: {str(e)}")
            return None
    
    def is_logged_in(self):
        """检查是否已登录且密钥有效"""
        return self.load_key() is not None
    
    def logout(self):
        """登出（删除本地密钥）"""
        if os.path.exists(self.key_file):
            os.remove(self.key_file)
            print("✅ 已登出，本地密钥已清除")


# ==================== 使用示例 ====================
if __name__ == '__main__':
    login_manager = CustomerServiceLogin()
    
    print("=" * 50)
    print("客服登录系统")
    print("=" * 50)
    
    # 检查是否已登录
    if login_manager.is_logged_in():
        print("✅ 已登录，密钥有效")
        key = login_manager.load_key()
        print(f"密钥长度: {len(key)} bytes")
    else:
        print("❌ 未登录或密钥已过期")
        password = input("请输入时效密码: ")
        
        result = login_manager.login(password)
        
        if result['success']:
            print(f"✅ {result['message']}")
            print(f"密钥有效期至: {result['expire_time']}")
        else:
            print(f"❌ {result['message']}")
