import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

print("1. 添加竞猜API路由...")

# 读取配置
stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-enabled/personal-website")
config = stdout.read().decode('utf-8')

# 在location /admin/之前插入
betting_config = """
    location /betting/ {
        proxy_pass http://127.0.0.1:5004/betting/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
    }

"""

if 'location /admin/' in config:
    new_config = config.replace('    location /admin/', betting_config + '    location /admin/')
    
    stdin, stdout, stderr = ssh.exec_command("cat > /etc/nginx/sites-enabled/personal-website << 'NGINXEOF'\n" + new_config + "\nNGINXEOF")
    stdout.read()
    print("   ✅ 配置已写入")
    
    stdin, stdout, stderr = ssh.exec_command("nginx -t")
    print(stdout.read().decode('utf-8'))
    print(stderr.read().decode('utf-8'))
    
    stdin, stdout, stderr = ssh.exec_command("nginx -s reload")
    print("   ✅ Nginx已重载")
else:
    print("❌ 未找到插入点")

print("\n2. 启动API服务(端口5004)...")
stdin, stdout, stderr = ssh.exec_command("pkill -f 'python3.*routes'")
stdout.read()

stdin, stdout, stderr = ssh.exec_command("cd /root/wallet/modules/betting_system && nohup python3 routes.py > /var/log/betting.log 2>&1 &")
stdout.read()

import time
time.sleep(2)

stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'python3.*routes' | grep -v grep")
print(stdout.read().decode('utf-8'))

ssh.close()
print("\n✅ 完成！请刷新前端测试")
