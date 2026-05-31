import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

print("1. 停止旧的API服务...")
stdin, stdout, stderr = ssh.exec_command("pkill -f 'python3 routes.py'")
stdout.read()
print("   ✅ 已停止")

print("2. 上传新代码...")
sftp = ssh.open_sftp()
sftp.put('f:/qianbao/betting_system/backend/routes.py', '/root/wallet/modules/betting_system/routes.py')
sftp.close()
print("   ✅ 上传成功")

print("3. 启动新的API服务...")
stdin, stdout, stderr = ssh.exec_command("cd /root/wallet/modules/betting_system && nohup python3 routes.py > /var/log/betting.log 2>&1 &")
stdout.read()
print("   ✅ 已启动")

print("4. 验证进程...")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'python.*routes' | grep -v grep")
result = stdout.read().decode('utf-8')
print(result)

ssh.close()
print("\n✅ 完成！")
