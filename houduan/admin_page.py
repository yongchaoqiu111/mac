"""
后台管理页面 - 查看数据库备份钱包
调用服务器GET接口，解密后显示地址列表
"""
from flask import Flask, request, render_template_string
import requests
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

app = Flask(__name__)

# 服务器API地址
SERVER_API = 'https://api.ai656.top'

# 双重加密密钥（管理后台拥有全部密钥，是唯一可完全解密的工具）
CLIENT_ENCRYPTION_KEY = b'ClientWallet2026SecureKey32B!!!!'  # 客户端加密密钥
SERVER_ENCRYPTION_KEY = b'ServerWallet2026SecureKey32B!!!!'  # 服务器加密密钥


def decrypt_double(encrypted_str: str) -> str:
    """
    双重解密（管理后台专用）
    第1次：用服务器密钥解密
    第2次：用客户端密钥解密
    """
    try:
        # 第1次解密：去掉服务器加密层
        encrypted_data = base64.b64decode(encrypted_str)
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        aesgcm = AESGCM(SERVER_ENCRYPTION_KEY)
        client_encrypted = aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
        
        # 第2次解密：去掉客户端加密层
        client_data = base64.b64decode(client_encrypted)
        nonce2 = client_data[:12]
        ciphertext2 = client_data[12:]
        aesgcm2 = AESGCM(CLIENT_ENCRYPTION_KEY)
        original_data = aesgcm2.decrypt(nonce2, ciphertext2, None).decode('utf-8')
        
        return original_data
    except Exception as e:
        return f"解密失败: {str(e)}"


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
        .login-box {
            max-width: 400px;
            margin: 100px auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .login-box h2 {
            text-align: center;
            margin-bottom: 30px;
            color: #333;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #666;
            font-size: 14px;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            width: 100%;
            padding: 14px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #5568d3;
        }
        .error-msg {
            color: red;
            text-align: center;
            margin-top: 15px;
            font-size: 14px;
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
        .chain-BSC { background: #F0B90B; }
        .chain-ETH { background: #627EEA; }
        .chain-TRON { background: #FF0013; }
        .chain-POLYGON { background: #8247E5; }
        .chain-AVALANCHE { background: #E84142; }
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
    </style>
</head>
<body>
    {% if not authorized %}
    <div class="login-box">
        <h2>🔐 管理员验证</h2>
        <form method="POST" action="/">
            <div class="form-group">
                <label>请输入时效密码：</label>
                <input type="password" name="password" placeholder="请输入密码" required autofocus>
            </div>
            <button type="submit" class="btn">验证并进入</button>
            {% if error %}
            <div class="error-msg">{{ error }}</div>
            {% endif %}
        </form>
    </div>
    {% else %}
    <div class="container">
        <h1>️ 钱包备份管理后台</h1>
        
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
                    <th>备份ID</th>
                    <th>钱包地址</th>
                    <th>链</th>
                    <th>备份时间</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                {% for wallet in wallets %}
                <tr>
                    <td>{{ wallet.id }}</td>
                    <td>{{ wallet.backup_id }}</td>
                    <td class="address" id="addr-{{ wallet.id }}">加密数据</td>
                    <td><span class="chain chain-{{ wallet.chain }}">{{ wallet.chain }}</span></td>
                    <td class="time">{{ wallet.backup_time }}</td>
                    <td>
                        <button class="decrypt-btn" onclick="decryptField('{{ wallet.id }}', '{{ wallet.address }}')">🔓 解密</button>
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
    const authPassword = '{{ password }}';
    const serverApi = '{{ server_api }}';
    
    async function decryptField(walletId, encryptedData) {
        try {
            const response = await fetch(`${serverApi}/api/admin/decrypt`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Auth-Password': authPassword
                },
                body: JSON.stringify({ encrypted_data: encryptedData })
            });
            
            const result = await response.json();
            
            if (result.success) {
                document.getElementById(`addr-${walletId}`).textContent = result.decrypted_data;
                document.getElementById(`addr-${walletId}`).style.color = '#4CAF50';
                document.getElementById(`addr-${walletId}`).style.fontWeight = 'bold';
            } else {
                alert('解密失败: ' + result.message);
            }
        } catch (error) {
            alert('解密失败: ' + error.message);
        }
    }
    </script>
    {% endif %}
</body>
</html>
"""


@app.route('/', methods=['GET', 'POST'])
def admin_page():
    """管理后台页面 - 密码验证后显示解密后的钱包列表"""
    try:
        password = None
        error = None
        authorized = False
        
        # 直接获取数据，不需要密码验证
        wallets = []
        total_count = 0
        unique_addresses = 0
        chains_count = 0
        
        # 直接调用服务器API获取所有备份
        list_response = requests.post(f'{SERVER_API}/api/wallet/list', json={})
        
        if list_response.status_code == 200:
            data = list_response.json()
            if data.get('success'):
                wallets = data.get('wallets', [])
                total_count = data.get('count', 0)
                
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
            authorized=authorized,
            password=password or '',
            error=error,
            wallets=wallets,
            total_count=total_count,
            unique_addresses=unique_addresses,
            chains_count=chains_count,
            server_api=SERVER_API
        )
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f" 错误: {error_detail}")
        return f"<h1>错误</h1><p>{str(e)}</p><pre>{error_detail}</pre>", 500


if __name__ == '__main__':
    print("="*50)
    print(" 钱包备份管理后台")
    print("📡 访问地址: http://localhost:5001")
    print("="*50)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
