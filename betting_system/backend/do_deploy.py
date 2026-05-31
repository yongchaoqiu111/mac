import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

print("1. 上传文件...")
sftp = ssh.open_sftp()
sftp.put('f:/qianbao/betting_system/backend/virtual_match_manager.py', '/root/wallet/modules/betting_system/virtual_match_manager.py')
sftp.close()
print("   ✅ 上传成功")

print("2. 清空今日数据...")
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"DELETE FROM team_daily_matches WHERE match_date = CURDATE(); DELETE FROM virtual_matches WHERE DATE(match_time) = CURDATE();\"")
stdout.read()
print("   ✅ 清空完成")

print("3. 重新生成比赛...")
stdin, stdout, stderr = ssh.exec_command("cd /root/wallet/modules/betting_system && python3 init_today_matches.py")
output = stdout.read().decode('utf-8')
error = stderr.read().decode('utf-8')
print(output)
if error:
    print("错误:", error)

print("4. 验证winner字段...")
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"SELECT id, game, match_time, winner FROM virtual_matches WHERE DATE(match_time) = CURDATE() ORDER BY match_time LIMIT 10;\"")
print(stdout.read().decode('utf-8'))

ssh.close()
print("\n✅ 全部完成！")
