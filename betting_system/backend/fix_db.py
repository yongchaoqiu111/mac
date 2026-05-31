import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

print("1. 清空并重新生成...")
stdin, stdout, stderr = ssh.exec_command("""mysql -uroot -p'WalletBackup2026!' wallet_backup -e "
DELETE FROM team_daily_matches WHERE match_date = CURDATE();
DELETE FROM virtual_matches WHERE DATE(match_time) = CURDATE();
"
""")
stdout.read()

stdin, stdout, stderr = ssh.exec_command("cd /root/wallet/modules/betting_system && python3 init_today_matches.py")
output = stdout.read().decode('utf-8')
print(output)

print("2. 验证状态...")
stdin, stdout, stderr = ssh.exec_command("""mysql -uroot -p'WalletBackup2026!' wallet_backup -e "
SELECT status, COUNT(*) as count FROM virtual_matches WHERE DATE(match_time) = CURDATE() GROUP BY status;
"
""")
print(stdout.read().decode('utf-8'))

print("3. 验证时间...")
stdin, stdout, stderr = ssh.exec_command("""mysql -uroot -p'WalletBackup2026!' wallet_backup -e "
SELECT id, game, TIME(match_time) as time, status FROM virtual_matches WHERE DATE(match_time) = CURDATE() ORDER BY match_time LIMIT 10;
"
""")
print(stdout.read().decode('utf-8'))

ssh.close()
print("\n✅ 完成！")
