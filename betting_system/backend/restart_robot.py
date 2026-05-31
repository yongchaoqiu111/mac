import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

print("1. 停止旧的裁判机器人...")
stdin, stdout, stderr = ssh.exec_command("pkill -f virtual_match_manager.py")
print("   ✅ 已停止")

print("2. 启动新的裁判机器人...")
stdin, stdout, stderr = ssh.exec_command("cd /root/wallet/modules/betting_system && nohup python3 virtual_match_manager.py > /var/log/virtual_matches.log 2>&1 &")
print("   ✅ 已启动")

print("3. 验证进程...")
import time
time.sleep(2)
stdin, stdout, stderr = ssh.exec_command("ps aux | grep virtual_match_manager | grep -v grep")
print(stdout.read().decode('utf-8'))

ssh.close()
print("✅ 完成！")
