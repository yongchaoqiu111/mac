import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

print("=== 检查比赛数据 ===\n")

# 1. 检查今日比赛数量
print("1. 今日比赛总数:")
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"SELECT COUNT(*) as total FROM virtual_matches WHERE DATE(match_time) = CURDATE();\"")
print(stdout.read().decode('utf-8'))

# 2. 检查未来比赛（应该显示的）
print("2. 未来比赛（match_time > NOW）:")
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"SELECT id, game, match_time, status FROM virtual_matches WHERE DATE(match_time) = CURDATE() AND match_time > NOW() ORDER BY match_time LIMIT 5;\"")
print(stdout.read().decode('utf-8'))

# 3. 检查API查询条件
print("3. API查询测试（pending且match_time > NOW）:")
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"SELECT id, game, TIME(match_time) as time, status FROM virtual_matches WHERE DATE(match_time) = CURDATE() AND status = 'pending' AND match_time > NOW() ORDER BY match_time LIMIT 10;\"")
print(stdout.read().decode('utf-8'))

# 4. 检查所有比赛状态分布
print("4. 比赛状态分布:")
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"SELECT status, COUNT(*) as count FROM virtual_matches WHERE DATE(match_time) = CURDATE() GROUP BY status;\"")
print(stdout.read().decode('utf-8'))

ssh.close()
