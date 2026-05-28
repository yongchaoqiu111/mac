"""
密钥分发服务器 - 提供密钥下载接口

安全机制：
1. 客服登录验证（固定密码 + 24小时时效）
2. 验证通过后返回会话ID
3. 使用会话ID下载密钥文件
4. 密钥文件存储在安全目录，不硬编码在代码中
"""
from flask import Flask, request, jsonify, send_file
import os
import json
from datetime import datetime
from time_limited_auth import auth_manager

app = Flask(__name__)

# 密钥文件路径（从环境变量读取）
KEY_FILE_PATH = os.environ.get('KEY_FILE_PATH', '/secure/keys/encryption_keys.json')


def load_keys_from_file():
    """从密钥文件加载"""
    if not os.path.exists(KEY_FILE_PATH):
        raise FileNotFoundError(f"密钥文件不存在: {KEY_FILE_PATH}")
    
    with open(KEY_FILE_PATH, 'r', encoding='utf-8') as f:
        keys = json.load(f)
    
    return keys


@app.route('/api/admin/verify_password', methods=['POST'])
def verify_password():
    """验证密码并创建会话"""
    try:
        data = request.get_json()
        if not data or 'password' not in data:
            return jsonify({'success': False, 'message': '缺少password参数'}), 400
        
        result = auth_manager.verify_password(data['password'])
        
        if result['valid']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'data': {
                    'session_id': result['session_id'],
                    'expire_time_str': result['expire_time_str']
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 401
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/admin/download_keys', methods=['GET'])
def download_keys():
    """下载密钥文件（需要有效会话）"""
    try:
        # 验证会话ID
        session_id = request.headers.get('X-Session-ID', '')
        if not session_id:
            return jsonify({'success': False, 'message': '缺少会话ID'}), 401
        
        verify_result = auth_manager.verify_session(session_id)
        if not verify_result['valid']:
            return jsonify({'success': False, 'message': verify_result['message']}), 401
        
        # 加载密钥文件
        keys = load_keys_from_file()
        
        # 记录审计日志
        log_download(session_id, request.remote_addr)
        
        # 返回密钥（JSON格式）
        return jsonify({
            'success': True,
            'message': '密钥下载成功',
            'data': keys,
            'downloaded_at': datetime.now().isoformat()
        }), 200
    
    except FileNotFoundError as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500


def log_download(session_id, ip_address):
    """记录密钥下载审计日志"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'session_id': session_id[:16] + '...',
        'ip_address': ip_address,
        'action': 'key_download'
    }
    
    log_file = 'audit_key_download.log'
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + '\n')


if __name__ == '__main__':
    print("="*60)
    print(" 密钥分发服务器")
    print("="*60)
    print(f"\n密钥文件路径: {KEY_FILE_PATH}")
    print(f"监听端口: 5002")
    print("\n⚠️  请确保密钥文件已创建且权限正确")
    print("\n启动服务...")
    
    app.run(host='0.0.0.0', port=5002, ssl_context='adhoc')  # 生产环境使用真实SSL证书
