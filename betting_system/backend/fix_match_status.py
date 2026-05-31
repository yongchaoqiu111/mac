import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

print("=== 手动执行close_betting ===\n")

# 1. 查询应该转为live的比赛
print("1. 查询应该转为live的比赛:")
stdin, stdout, stderr = ssh.exec_command("""mysql -uroot -p'WalletBackup2026!' wallet_backup -e "
SELECT id, game, match_time, status FROM virtual_matches 
WHERE status = 'pending' AND match_time <= NOW() + INTERVAL 2 MINUTE 
AND DATE(match_time) = CURDATE()
ORDER BY match_time;
"
""")
print(stdout.read().decode('utf-8'))

# 2. 执行更新
print("2. 执行更新:")
stdin, stdout, stderr = ssh.exec_command("""mysql -uroot -p'WalletBackup2026!' wallet_backup -e "
UPDATE virtual_matches 
SET status = 'live'
WHERE status = 'pending' AND match_time <= NOW() + INTERVAL 2 MINUTE 
AND DATE(match_time) = CURDATE();
SELECT ROW_COUNT() as affected;
"
""")
print(stdout.read().decode('utf-8'))

# 3. 查询状态统计
print("3. 各状态统计:")
stdin, stdout, stderr = ssh.exec_command("""mysql -uroot -p'WalletBackup2026!' wallet_backup -e "
SELECT status, COUNT(*) as count FROM virtual_matches 
WHERE DATE(match_time) = CURDATE() GROUP BY status;
"
""")
print(stdout.read().decode('utf-8'))

ssh.close()
