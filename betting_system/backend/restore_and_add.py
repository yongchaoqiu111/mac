import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

print("1. 从backup恢复配置...")
stdin, stdout, stderr = ssh.exec_command("cp /etc/nginx/sites-enabled/personal-website.bak /etc/nginx/sites-enabled/personal-website")
stdout.read()

print("2. 添加竞猜路由...")
stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-enabled/personal-website")
config = stdout.read().decode('utf-8')

# 插入竞猜路由
betting_route = """
    location /betting/ {
        proxy_pass http://127.0.0.1:5004/betting/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
    }

"""

if 'location /admin/' in config:
    new_config = config.replace('    location /admin/', betting_route + '    location /admin/')
    
    stdin, stdout, stderr = ssh.exec_command("echo '" + new_config.replace("'", "'\\''") + "' > /etc/nginx/sites-enabled/personal-website")
    stdout.read()
    
    print("   ✅ 配置已更新")
    
    stdin, stdout, stderr = ssh.exec_command("nginx -t")
    test_out = stdout.read().decode('utf-8')
    test_err = stderr.read().decode('utf-8')
    print("   测试:", test_out, test_err)
    
    if 'successful' in test_out or 'successful' in test_err:
        stdin, stdout, stderr = ssh.exec_command("nginx -s reload")
        print("   ✅ Nginx已重载")
    else:
        print("   ❌ 配置仍有错误")
else:
    print("   ❌ 未找到插入点")

ssh.close()
