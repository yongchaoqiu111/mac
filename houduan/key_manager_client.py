"""
客服密钥管理客户端 - 智能缓存 + 自动刷新

流程：
1. 检查本地密钥是否有效（未过期）
2. 如果有效，直接使用
3. 如果过期，重新登录并下载新密钥
4. 避免频繁请求服务器
"""
import requests
import os
import json
from datetime import datetime, timedelta


class KeyManagerClient:
    """密钥管理客户端"""
    
    def __init__(self, server_url='http://api.ai656.top:5002'):
        self.server_url = server_url
        self.key_cache_file = 'cached_keys.json'
        self.session_file = 'session_info.json'
    
    def get_keys(self, password=None):
        """
        获取解密密钥（智能缓存）
        
        Args:
            password: 固定密码（仅在需要重新登录时提供）
            
        Returns:
            {'client_key': bytes, 'server_key': bytes} 或 None
        """
        # 第1步：检查本地缓存是否有效
        cached_keys = self._load_cached_keys()
        if cached_keys:
            print("✅ 使用本地缓存密钥")
            return cached_keys
        
        # 第2步：缓存无效，需要重新登录
        if not password:
            print("❌ 密钥已过期，请提供密码重新登录")
            return None
        
        print("🔄 密钥已过期，正在重新登录...")
        
        # 第3步：登录获取会话ID
        session_result = self._login(password)
        if not session_result:
            return None
        
        session_id = session_result['session_id']
        expire_time_str = session_result['expire_time_str']
        
        print(f"✅ 登录成功，会话有效期至: {expire_time_str}")
        
        # 第4步：下载密钥
        keys = self._download_keys(session_id)
        if not keys:
            return None
        
        # 第5步：缓存密钥和会话信息
        self._cache_keys(keys, session_id, expire_time_str)
        
        print("✅ 密钥已缓存，24小时内无需重新登录")
        
        return keys
    
    def _login(self, password):
        """登录获取会话ID"""
        try:
            response = requests.post(
                f'{self.server_url}/api/admin/verify_password',
                json={'password': password},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ 登录失败: HTTP {response.status_code}")
                return None
            
            result = response.json()
            
            if not result.get('success'):
                print(f"❌ 登录失败: {result.get('message')}")
                return None
            
            return result.get('data')
        
        except Exception as e:
            print(f"❌ 登录异常: {str(e)}")
            return None
    
    def _download_keys(self, session_id):
        """下载密钥文件"""
        try:
            response = requests.get(
                f'{self.server_url}/api/admin/download_keys',
                headers={'X-Session-ID': session_id},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ 密钥下载失败: HTTP {response.status_code}")
                return None
            
            result = response.json()
            
            if not result.get('success'):
                print(f"❌ 密钥下载失败: {result.get('message')}")
                return None
            
            keys_data = result.get('data', {})
            
            # 转换为bytes
            client_key = keys_data['keys']['client_encryption_key'].encode('utf-8')
            server_key = keys_data['keys']['server_encryption_key'].encode('utf-8')
            
            return {
                'client_key': client_key,
                'server_key': server_key,
                'version': keys_data.get('version', 'v1'),
                'downloaded_at': result.get('downloaded_at')
            }
        
        except Exception as e:
            print(f"❌ 密钥下载异常: {str(e)}")
            return None
    
    def _cache_keys(self, keys, session_id, expire_time_str):
        """缓存密钥和会话信息"""
        # 解析过期时间
        try:
            expire_time = datetime.fromisoformat(expire_time_str)
        except:
            expire_time = datetime.now() + timedelta(hours=24)
        
        cache_data = {
            'client_key': keys['client_key'].hex(),
            'server_key': keys['server_key'].hex(),
            'session_id': session_id,
            'cached_at': datetime.now().isoformat(),
            'expire_time': expire_time.isoformat(),
            'version': keys.get('version', 'v1')
        }
        
        # 保存密钥缓存
        with open(self.key_cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)
        
        # 设置文件权限
        try:
            os.chmod(self.key_cache_file, 0o600)
        except:
            pass
    
    def _load_cached_keys(self):
        """加载缓存的密钥（检查是否过期）"""
        if not os.path.exists(self.key_cache_file):
            return None
        
        try:
            with open(self.key_cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 检查是否过期
            expire_time = datetime.fromisoformat(cache_data['expire_time'])
            if datetime.now() >= expire_time:
                print(f"⚠️  缓存密钥已过期（{expire_time}）")
                os.remove(self.key_cache_file)
                return None
            
            # 检查会话是否仍然有效（可选，增加安全性）
            # session_result = self._verify_session(cache_data['session_id'])
            # if not session_result:
            #     return None
            
            # 返回密钥
            client_key = bytes.fromhex(cache_data['client_key'])
            server_key = bytes.fromhex(cache_data['server_key'])
            
            print(f"✅ 缓存密钥有效，剩余时间: {expire_time - datetime.now()}")
            
            return {
                'client_key': client_key,
                'server_key': server_key,
                'version': cache_data.get('version', 'v1')
            }
        
        except Exception as e:
            print(f"❌ 加载缓存密钥失败: {str(e)}")
            if os.path.exists(self.key_cache_file):
                os.remove(self.key_cache_file)
            return None
    
    def _verify_session(self, session_id):
        """验证会话是否仍然有效（可选）"""
        try:
            response = requests.get(
                f'{self.server_url}/api/admin/verify_session',
                headers={'X-Session-ID': session_id},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('valid', False)
            
            return False
        
        except:
            return False
    
    def clear_cache(self):
        """清除缓存（强制重新登录）"""
        for file in [self.key_cache_file, self.session_file]:
            if os.path.exists(file):
                os.remove(file)
        print("✅ 缓存已清除")


# ==================== 使用示例 ====================
if __name__ == '__main__':
    client = KeyManagerClient()
    
    print("="*60)
    print(" 客服密钥管理客户端测试")
    print("="*60)
    
    # 第1次调用：需要登录
    print("\n【第1次获取密钥】")
    keys = client.get_keys(password='customer_service_2026')
    
    if keys:
        print(f"客户端密钥长度: {len(keys['client_key'])} bytes")
        print(f"服务器密钥长度: {len(keys['server_key'])} bytes")
    
    # 第2次调用：使用缓存
    print("\n【第2次获取密钥（应使用缓存）】")
    keys = client.get_keys()  # 不需要密码
    
    if keys:
        print(f"✅ 成功从缓存加载密钥")
    
    # 清除缓存测试
    print("\n【清除缓存后重新获取】")
    client.clear_cache()
    keys = client.get_keys(password='customer_service_2026')
    
    if keys:
        print(f"✅ 重新登录并下载密钥成功")
