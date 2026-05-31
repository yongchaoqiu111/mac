import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

print("1. 读取当前配置...")
stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-enabled/personal-website")
current_config = stdout.read().decode('utf-8')

# 在location /admin/之前插入竞猜API路由
betting_routes = """
    # 竞猜API路由
    location /betting/ {
        proxy_pass http://127.0.0.1:5004/betting/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
    }

"""

# 找到/admin/位置并插入
insert_point = current_config.find('    location /admin/')
if insert_point != -1:
    new_config = current_config[:insert_point] + betting_routes + current_config[insert_point:]
    
    print("2. 写入新配置...")
    stdin, stdout, stderr = ssh.exec_command(f"cat > /etc/nginx/sites-enabled/personal-website << 'EOF'\n{new_config}\nEOF")
    stdout.read()
    print("   ✅ 配置已更新")
    
    print("3. 测试配置...")
    stdin, stdout, stderr = ssh.exec_command("nginx -t")
    test_result = stdout.read().decode('utf-8')
    test_error = stderr.read().decode('utf-8')
    print(test_result)
    if test_error:
        print(test_error)
    
    print("4. 重载Nginx...")
    stdin, stdout, stderr = ssh.exec_command("nginx -s reload")
    stdout.read()
    print("   ✅ Nginx已重载")
else:
    print("❌ 未找到插入点")

ssh.close()
print("\n✅ 完成！")
