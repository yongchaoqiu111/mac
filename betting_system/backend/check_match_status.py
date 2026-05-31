import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

print("=== 检查比赛状态 ===\n")

# 1. 服务器时间和日期
print("1. 服务器时间:")
stdin, stdout, stderr = ssh.exec_command("date && date +%Y-%m-%d")
print(stdout.read().decode('utf-8'))

# 2. 查询所有比赛按状态统计
print("2. 各状态比赛数量:")
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"SELECT status, COUNT(*) as count FROM virtual_matches WHERE DATE(match_time) = CURDATE() GROUP BY status;\"")
print(stdout.read().decode('utf-8'))

# 3. 查看已结束的比赛
print("3. 已结束的比赛（前5场）:")
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"SELECT id, game, match_time, status, winner FROM virtual_matches WHERE DATE(match_time) = CURDATE() AND status = 'finished' ORDER BY match_time LIMIT 5;\"")
print(stdout.read().decode('utf-8'))

# 4. 查看进行中的比赛
print("4. 进行中的比赛:")
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"SELECT id, game, match_time, status FROM virtual_matches WHERE DATE(match_time) = CURDATE() AND status = 'live' LIMIT 5;\"")
print(stdout.read().decode('utf-8'))

ssh.close()
