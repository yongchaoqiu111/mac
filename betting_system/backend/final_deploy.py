import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

print("1. 上传routes.py...")
sftp = ssh.open_sftp()
sftp.put('f:/qianbao/betting_system/backend/routes.py', '/root/wallet/modules/betting_system/routes.py')
sftp.put('f:/qianbao/betting_system/backend/virtual_match_manager.py', '/root/wallet/modules/betting_system/virtual_match_manager.py')
sftp.close()
print("   ✅ 上传成功")

print("2. 重启API服务...")
stdin, stdout, stderr = ssh.exec_command("pkill -f 'python3.*routes'")
stdout.read()
stdin, stdout, stderr = ssh.exec_command("cd /root/wallet/modules/betting_system && nohup python3 routes.py > /var/log/betting.log 2>&1 &")
stdout.read()
print("   ✅ API已重启")

print("3. 重启裁判机器人...")
stdin, stdout, stderr = ssh.exec_command("pkill -f 'python3.*virtual_match'")
stdout.read()
stdin, stdout, stderr = ssh.exec_command("cd /root/wallet/modules/betting_system && nohup python3 virtual_match_manager.py > /var/log/virtual_matches.log 2>&1 &")
stdout.read()
print("   ✅ 机器人已重启")

print("4. 验证进程...")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'python3' | grep -E 'routes|virtual_match' | grep -v grep")
result = stdout.read().decode('utf-8')
print(result)

ssh.close()
print("\n✅ 全部完成！")
