import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

print("1. 上传文件...")
sftp = ssh.open_sftp()
sftp.put('f:/qianbao/betting_system/backend/virtual_match_manager.py', '/root/wallet/modules/betting_system/virtual_match_manager.py')
sftp.close()
print("   ✅ 上传成功")

print("2. 重启裁判机器人...")
stdin, stdout, stderr = ssh.exec_command("pkill -f 'python3.*virtual_match'")
stdout.read()

stdin, stdout, stderr = ssh.exec_command("cd /root/wallet/modules/betting_system && nohup python3 virtual_match_manager.py > /var/log/virtual_matches.log 2>&1 &")
stdout.read()
print("   ✅ 已重启")

print("3. 验证进程...")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'python3.*virtual_match' | grep -v grep")
result = stdout.read().decode('utf-8')
print(result)

ssh.close()
print("\n✅ 完成！")
