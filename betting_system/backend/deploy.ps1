# PowerShell部署脚本
$script = @"
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.242.108.37', username='root', password='Wallet2026!Backup')

# 上传文件
sftp = ssh.open_sftp()
sftp.put('f:/qianbao/betting_system/backend/virtual_match_manager_new.py', '/root/wallet/modules/betting_system/virtual_match_manager.py')
sftp.close()
print('文件上传成功')

# 清空今日数据
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e 'DELETE FROM team_daily_matches WHERE match_date = CURDATE(); DELETE FROM virtual_matches WHERE DATE(match_time) = CURDATE();'")
print('清空完成')

# 重新生成
stdin, stdout, stderr = ssh.exec_command('cd /root/wallet/modules/betting_system && python3 init_today_matches.py')
output = stdout.read().decode('utf-8')
print(output)

# 验证
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e 'SELECT COUNT(*) as total, game, TIME(match_time) as time FROM virtual_matches WHERE DATE(match_time) = CURDATE() ORDER BY time LIMIT 10;'")
print(stdout.read().decode('utf-8'))

ssh.close()
print('部署完成！')
"@

python -c $script
