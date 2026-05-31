"""
钱包系统API路由
功能: 钱包列表、备份、删除、解密
独立模块，可单独部署
"""
from flask import Blueprint, jsonify, request
import pymysql
import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

wallet_bp = Blueprint('wallet', __name__)

# 数据库配置
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'WalletBackup2026!'),
    'database': os.environ.get('DB_NAME', 'wallet_backup'),
    'charset': 'utf8mb4'
}

# 加密密钥
SERVER_KEY = b'ServerWallet2026SecureKey32B!!!!'


def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)


@wallet_bp.route('/api/wallet/list', methods=['POST'])
def list_wallets():
    """列出所有钱包"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT id, address, chain, encrypted_data, created_at FROM wallets ORDER BY created_at DESC')
        wallets = cursor.fetchall()
        conn.close()
        return jsonify({
            'success': True,
            'wallets': wallets
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@wallet_bp.route('/api/wallet/backup', methods=['POST'])
def backup_wallet():
    """备份钱包"""
    try:
        data = request.get_json(force=True)
        address = data.get('address')
        chain = data.get('chain')
        encrypted_data = data.get('encrypted_data')
        
        if not all([address, chain, encrypted_data]):
            return jsonify({'success': False, 'message': '参数不完整'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO wallets (address, chain, encrypted_data) VALUES (%s, %s, %s)',
            (address, chain, encrypted_data)
        )
        wallet_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'wallet_id': wallet_id,
            'message': '备份成功'
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@wallet_bp.route('/api/wallet/delete', methods=['POST'])
def delete_wallet():
    """删除钱包"""
    try:
        data = request.get_json(force=True)
        address = data.get('address')
        
        if not address:
            return jsonify({'success': False, 'message': '缺少address参数'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM wallets WHERE address = %s', (address,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'deleted': deleted_count,
            'message': f'删除了 {deleted_count} 个钱包'
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@wallet_bp.route('/api/wallet/decrypt', methods=['POST'])
def decrypt_wallet():
    """解密钱包数据"""
    try:
        data = request.get_json(force=True)
        encrypted_data = data.get('encrypted_data')
        
        if not encrypted_data:
            return jsonify({'success': False, 'message': '缺少encrypted_data参数'}), 400
        
        # Base64解码
        encrypted_bytes = base64.b64decode(encrypted_data)
        
        # 提取nonce和ciphertext
        nonce = encrypted_bytes[:12]
        ciphertext = encrypted_bytes[12:]
        
        # 使用服务器密钥解密
        aesgcm = AESGCM(SERVER_KEY)
        decrypted_json = aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
        
        return jsonify({
            'success': True,
            'wallet_data': decrypted_json
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'解密失败: {str(e)}'}), 500
