"""
时效密码管理系统 - 客服解密权限控制
生成时效密码 → 验证密码 → 授权解密
"""
import hashlib
import time
from datetime import datetime


class TimeLimitedAuth:
    """时效密码管理器"""
    
    def __init__(self, fixed_password='customer_service_2026'):
        """
        初始化管理器
        
        Args:
            fixed_password: 固定密码（生产环境从环境变量读取）
        """
        self.fixed_password = fixed_password
        self.sessions = {}  # {session_id: {'login_time': timestamp, 'expire_time': timestamp}}
    
    def verify_password(self, password):
        """
        验证密码并创建会话（有时效性）
        
        Args:
            password: 用户输入的密码
            hours: 有效期（小时），默认24小时
            
        Returns:
            {'valid': True/False, 'message': '提示信息', 'session_id': str, 'expire_time_str': str}
        """
        import secrets
        import time
        from datetime import datetime
        
        # 验证固定密码
        if password != self.fixed_password:
            return {'valid': False, 'message': '密码错误'}
        
        # 生成会话ID
        session_id = secrets.token_urlsafe(32)
        
        # 计算过期时间（24小时）
        hours = 24
        login_time = time.time()
        expire_time = login_time + (hours * 3600)
        expire_datetime = datetime.fromtimestamp(expire_time)
        
        # 存储会话信息
        self.sessions[session_id] = {
            'login_time': login_time,
            'expire_time': expire_time,
            'password_used': password[:8] + '***'  # 脱敏记录
        }
        
        return {
            'valid': True,
            'message': '验证成功',
            'session_id': session_id,
            'expire_time': expire_time,
            'expire_time_str': expire_datetime.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def verify_session(self, session_id):
        """
        验证会话是否有效
        
        Args:
            session_id: 会话ID
            
        Returns:
            {'valid': True/False, 'message': str}
        """
        import time
        
        if session_id not in self.sessions:
            return {'valid': False, 'message': '会话不存在'}
        
        session_info = self.sessions[session_id]
        
        # 检查是否过期
        if time.time() > session_info['expire_time']:
            # 清理过期会话
            del self.sessions[session_id]
            return {'valid': False, 'message': '会话已过期，请重新登录'}
        
        return {'valid': True, 'message': '会话有效'}


# 全局实例（使用环境变量中的数据库密码）
import os
auth_manager = TimeLimitedAuth(fixed_password=os.environ.get('DB_PASSWORD', 'customer_service_2026'))


if __name__ == '__main__':
    # 测试
    print("="*50)
    print(" 时效密码系统测试 - 固定密码+会话时效")
    print("="*50)
    
    auth = TimeLimitedAuth(fixed_password='test_password_123')
    
    # 1. 验证正确密码
    print("\n【验证正确密码】")
    result = auth.verify_password('test_password_123')
    print(f"结果: {result['valid']}")
    print(f"会话ID: {result['session_id'][:16]}...")
    print(f"过期时间: {result['expire_time_str']}")
    
    # 2. 验证错误密码
    print("\n【验证错误密码】")
    result = auth.verify_password('wrong_password')
    print(f"结果: {result['valid']} - {result['message']}")
    
    # 3. 验证会话
    print("\n【验证会话有效性】")
    session_result = auth.verify_session(result.get('session_id', ''))
    print(f"结果: {session_result}")
    
    print("\n" + "="*50)
