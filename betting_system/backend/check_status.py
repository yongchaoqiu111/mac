import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

print("=== 检查队伍和比赛 ===\n")

# 1. 检查每个游戏的队伍数量
print("1. 队伍数量:")
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"SELECT game, COUNT(*) as team_count FROM virtual_teams GROUP BY game;\"")
print(stdout.read().decode('utf-8'))

# 2. 检查今日比赛分布
print("2. 今日比赛时间分布（前10场）:")
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"SELECT game, TIME(match_time) as time, status FROM virtual_matches WHERE DATE(match_time) = CURDATE() ORDER BY match_time LIMIT 10;\"")
print(stdout.read().decode('utf-8'))

# 3. 统计每个游戏的比赛数
print("3. 各游戏比赛数量:")
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"SELECT game, COUNT(*) as match_count FROM virtual_matches WHERE DATE(match_time) = CURDATE() GROUP BY game;\"")
print(stdout.read().decode('utf-8'))

ssh.close()
