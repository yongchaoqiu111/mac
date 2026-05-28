"""
密钥分段传输系统 - 双重验证 + 分段下载

安全机制：
1. 第1段密钥：密码验证后获取（存储在服务器A）
2. 第2段密钥：二次验证后获取（存储在服务器B）
3. 只有同时拥有两段密钥才能完成解密
4. 单段密钥毫无价值
"""
import requests
import os
import json
from datetime import datetime


class SplitKeyLogin:
    """分段密钥登录管理器"""
    
    def __init__(self, server_a='http://api.ai656.top', server_b='http://backup.ai656.top'):
        self.server_a = server_a  # 主服务器
        self.server_b = server_b  # 备份服务器（存储第2段密钥）
        self.key_file = 'split_keys.json'
    
    def login_step1(self, password):
        """
        第1步：验证密码，获取第1段密钥
        
        Returns:
            {'success': bool, 'message': str, 'key_part1': str}
        """
        try:
            response = requests.post(
                f'{self.server_a}/api/admin/verify_password',
                json={'password': password},
                timeout=10
            )
            
            if response.status_code != 200:
                return {'success': False, 'message': f'服务器错误: {response.status_code}'}
            
            result = response.json()
            
            if not result.get('success'):
                return {'success': False, 'message': result.get('message', '密码错误')}
            
            # 获取第1段密钥
            key_part1 = result.get('data', {}).get('key_part1', '')
            
            if not key_part1:
                return {'success': False, 'message': '第1段密钥获取失败'}
            
            # 临时保存
            self._save_temp_key('part1', key_part1)
            
            return {
                'success': True,
                'message': '第1步验证成功',
                'key_part1': key_part1
            }
        
        except Exception as e:
            return {'success': False, 'message': f'第1步失败: {str(e)}'}
    
    def login_step2(self, verification_code):
        """
        第2步：二次验证，获取第2段密钥
        
        Args:
            verification_code: 二次验证码（短信/邮箱/TOTP）
            
        Returns:
            {'success': bool, 'message': str, 'complete_key': bytes}
        """
        try:
            # 检查是否有第1段密钥
            part1 = self._load_temp_key('part1')
            if not part1:
                return {'success': False, 'message': '请先完成第1步验证'}
            
            # 从备份服务器获取第2段密钥
            response = requests.post(
                f'{self.server_b}/api/admin/get_key_part2',
                json={
                    'verification_code': verification_code,
                    'session_id': self._get_session_id()
                },
                timeout=10
            )
            
            if response.status_code != 200:
                return {'success': False, 'message': f'第2步服务器错误: {response.status_code}'}
            
            result = response.json()
            
            if not result.get('success'):
                return {'success': False, 'message': result.get('message', '二次验证失败')}
            
            key_part2 = result.get('key_part2', '')
            
            # 合并两段密钥
            complete_key = self._merge_keys(part1, key_part2)
            
            # 保存完整密钥
            self._save_complete_key(complete_key)
            
            # 清理临时文件
            self._cleanup_temp_keys()
            
            return {
                'success': True,
                'message': '登录成功，完整密钥已下载',
                'complete_key': complete_key
            }
        
        except Exception as e:
            return {'success': False, 'message': f'第2步失败: {str(e)}'}
    
    def _merge_keys(self, part1: str, part2: str) -> bytes:
        """
        合并两段密钥
        
        策略：XOR异或运算，确保单段密钥无意义
        """
        key1_bytes = part1.encode('utf-8')
        key2_bytes = part2.encode('utf-8')
        
        # XOR合并
        merged = bytes([a ^ b for a, b in zip(key1_bytes, key2_bytes)])
        
        return merged
    
    def _save_temp_key(self, part_name: str, key_data: str):
        """保存临时密钥片段"""
        temp_file = f'temp_{part_name}.json'
        data = {
            'key': key_data,
            'timestamp': datetime.now().isoformat(),
            'session_id': self._get_session_id()
        }
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        
        os.chmod(temp_file, 0o600)
    
    def _load_temp_key(self, part_name: str) -> str:
        """加载临时密钥片段"""
        temp_file = f'temp_{part_name}.json'
        
        if not os.path.exists(temp_file):
            return None
        
        try:
            with open(temp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查是否过期（10分钟）
            timestamp = datetime.fromisoformat(data['timestamp'])
            minutes_passed = (datetime.now() - timestamp).total_seconds() / 60
            
            if minutes_passed > 10:
                os.remove(temp_file)
                return None
            
            return data['key']
        
        except:
            return None
    
    def _save_complete_key(self, complete_key: bytes):
        """保存完整密钥"""
        save_data = {
            'key_n': complete_key.hex(),  # 转为hex存储
            'login_time': datetime.now().isoformat(),
            'server_a': self.server_a,
            'server_b': self.server_b
        }
        
        with open(self.key_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        os.chmod(self.key_file, 0o600)
    
    def load_key(self) -> bytes:
        """加载完整密钥"""
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
            
            key_hex = data.get('key_n', '')
            if key_hex:
                return bytes.fromhex(key_hex)
            
            return None
        
        except Exception as e:
            print(f"❌ 加载密钥失败: {str(e)}")
            return None
    
    def _get_session_id(self) -> str:
        """生成会话ID"""
        import hashlib
        import time
        session_str = f"{self.server_a}_{time.time()}"
        return hashlib.md5(session_str.encode()).hexdigest()[:16]
    
    def _cleanup_temp_keys(self):
        """清理临时密钥文件"""
        for part in ['part1', 'part2']:
            temp_file = f'temp_{part}.json'
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self.load_key() is not None
    
    def logout(self):
        """登出"""
        self._cleanup_temp_keys()
        if os.path.exists(self.key_file):
            os.remove(self.key_file)
            print("✅ 已登出，密钥已清除")


# ==================== 使用示例 ====================
if __name__ == '__main__':
    login_manager = SplitKeyLogin()
    
    print("=" * 60)
    print("分段密钥登录系统 - 双重验证")
    print("=" * 60)
    
    if login_manager.is_logged_in():
        print("✅ 已登录，密钥有效")
        key = login_manager.load_key()
        print(f"密钥长度: {len(key)} bytes")
    else:
        print("\n【第1步】密码验证")
        password = input("请输入时效密码: ")
        
        result1 = login_manager.login_step1(password)
        
        if result1['success']:
            print(f"✅ {result1['message']}")
            
            print("\n【第2步】二次验证")
            code = input("请输入二次验证码: ")
            
            result2 = login_manager.login_step2(code)
            
            if result2['success']:
                print(f"✅ {result2['message']}")
                print(f"完整密钥长度: {len(result2['complete_key'])} bytes")
            else:
                print(f"❌ {result2['message']}")
        else:
            print(f"❌ {result1['message']}")
