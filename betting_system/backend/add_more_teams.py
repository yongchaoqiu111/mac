import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

# 查看各游戏可用队伍数（未在今日出场的）
print("各游戏可用队伍数:")
stdin, stdout, stderr = ssh.exec_command("""mysql -uroot -p'WalletBackup2026!' wallet_backup -e "
SELECT vt.game, COUNT(*) as available 
FROM virtual_teams vt
LEFT JOIN team_daily_matches tdm ON vt.id = tdm.team_id AND tdm.match_date = CURDATE()
WHERE tdm.id IS NULL
GROUP BY vt.game;
" """)
print(stdout.read().decode('utf-8'))

# 添加DOTA2队伍
dota2_teams = [
    "Ancient Defenders", "Roshan Slayers", "Divine Rapier",
    "Aegis Holders", "Mega Creeps", "Buyback Kings",
    "Smoke Gankers", "TP Escape", "BKB Rush",
    "Dagon Burst", "Hex Masters", "Scythe Carriers",
    "Refresher Duo", "Boots of Travel", "Flying Courier",
    "Observer Ward", "Sentry Dusters", "Gem Carriers",
]

for name in dota2_teams:
    stdin, stdout, stderr = ssh.exec_command(f"mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"INSERT INTO virtual_teams (game, team_name) VALUES ('dota2', '{name}');\"")
    print(f"添加DOTA2: {name}")

# 再添加一些CSGO队伍
csgo_extra = [
    "Defuse Kit", "Bomb Carrier", "Plant Kings",
    "Retake Squad", "Hold Site", "Rotate Fast",
    "Callouts Pro", "Economy Masters", "Bonus Round",
]

for name in csgo_extra:
    stdin, stdout, stderr = ssh.exec_command(f"mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"INSERT INTO virtual_teams (game, team_name) VALUES ('csgo', '{name}');\"")
    print(f"添加CSGO: {name}")

# 重新检查
print("\n添加后可用队伍数:")
stdin, stdout, stderr = ssh.exec_command("""mysql -uroot -p'WalletBackup2026!' wallet_backup -e "
SELECT vt.game, COUNT(*) as available 
FROM virtual_teams vt
LEFT JOIN team_daily_matches tdm ON vt.id = tdm.team_id AND tdm.match_date = CURDATE()
WHERE tdm.id IS NULL
GROUP BY vt.game;
" """)
print(stdout.read().decode('utf-8'))

ssh.close()
