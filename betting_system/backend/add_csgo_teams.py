import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

# 查看CSGO现有队伍
print("CSGO现有队伍:")
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"SELECT team_name FROM virtual_teams WHERE game='csgo' ORDER BY id;\"")
print(stdout.read().decode('utf-8'))

# 添加更多CSGO队伍（从其他游戏的队伍名改编）
csgo_teams = [
    ("csgo", "AK47 Masters"),
    ("csgo", "AWP Snipers"),
    ("csgo", "Deagle Kings"),
    ("csgo", "M4A4 Elites"),
    ("csgo", "Glock Force"),
    ("csgo", "USP Legends"),
    ("csgo", "P90 Rushers"),
    ("csgo", "MP7 Streak"),
    ("csgo", "Nova Bombers"),
    ("csgo", "Famas Warriors"),
]

for game, name in csgo_teams:
    stdin, stdout, stderr = ssh.exec_command(f"mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"INSERT INTO virtual_teams (game, team_name) VALUES ('{game}', '{name}');\"")
    print(f"添加: {name}")

# 重新检查数量
print("\n添加后各游戏队伍数量:")
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e \"SELECT game, COUNT(*) as count FROM virtual_teams GROUP BY game;\"")
print(stdout.read().decode('utf-8'))

ssh.close()
