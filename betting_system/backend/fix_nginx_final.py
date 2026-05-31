import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

# 创建正确的Nginx配置
config = """server {
    listen 80;
    server_name chaseqiu.top www.chaseqiu.top ai656.top www.ai656.top api.ai656.top;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name chaseqiu.top www.chaseqiu.top ai656.top www.ai656.top api.ai656.top;

    ssl_certificate /etc/letsencrypt/live/chaseqiu.top/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/chaseqiu.top/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location /666/ {
        root /opt/personal-website;
        index index.html;
        try_files $uri $uri/ /666/index.html;
    }

    location / {
        root /opt/personal-website/frontend;
        try_files $uri $uri/ /index.html;
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:5001/admin/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
    }

    location /betting/ {
        proxy_pass http://127.0.0.1:5004/betting/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
    }
}
"""

print("1. 写入Nginx配置...")
stdin, stdout, stderr = ssh.exec_command(f"cat > /etc/nginx/sites-enabled/personal-website << 'EOF'\n{config}\nEOF")
stdout.read()
stderr.read()

print("2. 测试配置...")
stdin, stdout, stderr = ssh.exec_command("nginx -t")
test_output = stderr.read().decode('utf-8')
print(test_output)

if 'successful' in test_output or 'ok' in test_output:
    print("3. 重载Nginx...")
    stdin, stdout, stderr = ssh.exec_command("nginx -s reload")
    stdout.read()
    print("✅ Nginx配置更新成功")
else:
    print("❌ Nginx配置有错误")

print("\n4. 启动竞猜API服务...")
stdin, stdout, stderr = ssh.exec_command("pkill -f 'python3.*routes.py'")
stdout.read()

stdin, stdout, stderr = ssh.exec_command("cd /root/wallet/modules/betting_system && nohup python3 routes.py > /var/log/betting.log 2>&1 &")
stdout.read()

print("5. 等待服务启动...")
import time
time.sleep(2)

print("6. 验证进程...")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'python3.*routes' | grep -v grep")
process_output = stdout.read().decode('utf-8')
print(process_output if process_output else "未找到进程")

print("7. 检查端口...")
stdin, stdout, stderr = ssh.exec_command("netstat -tlnp | grep 5004")
port_output = stdout.read().decode('utf-8')
print(port_output if port_output else "端口5004未监听")

ssh.close()
print("\n✅ 完成！现在可以测试API了")
