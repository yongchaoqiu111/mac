import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

print("1. 读取当前配置...")
stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-enabled/personal-website")
current_config = stdout.read().decode('utf-8')

# 显示配置片段
print("当前配置片段：")
for i, line in enumerate(current_config.split('\n')):
    if 'admin' in line.lower() or 'webhook' in line.lower():
        print(f"{i}: {line}")

ssh.close()
