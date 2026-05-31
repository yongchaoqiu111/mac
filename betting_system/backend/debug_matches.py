import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

print("=== 详细检查 ===\n")

# 1. 查看所有24小时中哪些有比赛
print("1. 每小时比赛情况:")
stdin, stdout, stderr = ssh.exec_command("""mysql -uroot -p'WalletBackup2026!' wallet_backup -e "
SELECT 
    DATE_FORMAT(match_time, '%%H:00') as hour,
    game,
    COUNT(*) as matches
FROM virtual_matches 
WHERE DATE(match_time) = CURDATE()
GROUP BY DATE_FORMAT(match_time, '%%H:00'), game
ORDER BY hour;
" """)
print(stdout.read().decode('utf-8'))

# 2. 检查没有比赛的小时
print("2. 没有比赛的小时:")
stdin, stdout, stderr = ssh.exec_command("""mysql -uroot -p'WalletBackup2026!' wallet_backup -e "
SELECT 
    CONCAT(LPAD(h.hour, 2, '0'), ':00') as missing_hour
FROM (
    SELECT 0 as hour UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
    UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 UNION SELECT 11
    UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15 UNION SELECT 16 UNION SELECT 17
    UNION SELECT 18 UNION SELECT 19 UNION SELECT 20 UNION SELECT 21 UNION SELECT 22 UNION SELECT 23
) h
LEFT JOIN virtual_matches vm ON HOUR(vm.match_time) = h.hour AND DATE(vm.match_time) = CURDATE()
WHERE vm.id IS NULL
ORDER BY h.hour;
" """)
print(stdout.read().decode('utf-8'))

# 3. 检查各游戏已使用的队伍
print("3. 各游戏已出场队伍数:")
stdin, stdout, stderr = ssh.exec_command("""mysql -uroot -p'WalletBackup2026!' wallet_backup -e "
SELECT vt.game, COUNT(DISTINCT vt.id) as used_teams
FROM virtual_matches vm
JOIN virtual_teams vt ON (vm.team_a_id = vt.id OR vm.team_b_id = vt.id)
WHERE DATE(vm.match_time) = CURDATE()
GROUP BY vt.game;
" """)
print(stdout.read().decode('utf-8'))

ssh.close()
