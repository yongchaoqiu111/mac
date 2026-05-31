import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

print("修复Nginx配置...")

# 读取当前配置
stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-enabled/personal-website")
config_lines = stdout.readlines()

# 找到location /admin/的位置
insert_idx = -1
for i, line in enumerate(config_lines):
    if 'location /admin/' in line:
        insert_idx = i
        break

if insert_idx > 0:
    # 插入竞猜路由
    betting_lines = [
        "\n",
        "    location /betting/ {\n",
        "        proxy_pass http://127.0.0.1:5004/betting/;\n",
        "        proxy_set_header Host $host;\n",
        "        proxy_set_header X-Real-IP $remote_addr;\n",
        "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n",
        "        proxy_http_version 1.1;\n",
        "    }\n",
    ]
    
    new_config = config_lines[:insert_idx] + betting_lines + config_lines[insert_idx:]
    
    # 写入文件
    config_text = ''.join(new_config)
    stdin, stdout, stderr = ssh.exec_command(f"cat > /tmp/nginx_conf << 'EOF'\n{config_text}\nEOF")
    stdout.read()
    
    stdin, stdout, stderr = ssh.exec_command("mv /tmp/nginx_conf /etc/nginx/sites-enabled/personal-website")
    stdout.read()
    
    print("✅ 配置已修复")
    
    # 测试
    stdin, stdout, stderr = ssh.exec_command("nginx -t")
    print("Nginx测试:", stdout.read().decode('utf-8'), stderr.read().decode('utf-8'))
    
    stdin, stdout, stderr = ssh.exec_command("nginx -s reload")
    print("✅ Nginx已重载")
else:
    print("❌ 未找到插入点")

ssh.close()
