import paramiko

# SSH连接
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('服务器IP', username='root', password='密码')

# 上传文件
sftp = ssh.open_sftp()
sftp.put('f:/qianbao/betting_system/backend/virtual_match_manager_new.py', '/root/wallet/modules/betting_system/virtual_match_manager.py')
sftp.close()
print("✅ 文件上传成功")

# 清空今日比赛数据
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'密码' wallet_backup -e \"DELETE FROM team_daily_matches WHERE match_date = CURDATE(); DELETE FROM virtual_matches WHERE DATE(match_time) = CURDATE();\"")
print(stdout.read().decode('utf-8'))

# 重新生成
stdin, stdout, stderr = ssh.exec_command("cd /root/wallet/modules/betting_system && python3 init_today_matches.py")
output = stdout.read().decode('utf-8')
print(output)

# 验证
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'密码' wallet_backup -e \"SELECT COUNT(*) as total, game, DATE(match_time) as date FROM virtual_matches WHERE DATE(match_time) = CURDATE() GROUP BY game;\"")
print(stdout.read().decode('utf-8'))

ssh.close()
print("✅ 完成！")
