import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

print("=== 检查0点比赛状态 ===\n")

# 查询0点的比赛
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"SELECT id, game, match_time, status, winner FROM virtual_matches WHERE DATE(match_time) = CURDATE() AND TIME(match_time) < '02:00:00' ORDER BY match_time;\"")
result = stdout.read().decode('utf-8')
print(result)

print("\n=== 各状态统计 ===\n")
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"SELECT status, COUNT(*) as count FROM virtual_matches WHERE DATE(match_time) = CURDATE() GROUP BY status;\"")
print(stdout.read().decode('utf-8'))

ssh.close()
