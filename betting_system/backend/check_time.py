import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

print("服务器时间:")
stdin, stdout, stderr = ssh.exec_command("date")
print(stdout.read().decode('utf-8'))

print("今日比赛完整列表:")
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"SELECT id, game, match_time FROM virtual_matches WHERE DATE(match_time) = CURDATE() ORDER BY match_time;\"")
print(stdout.read().decode('utf-8'))

ssh.close()
