import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('47.83.0.101', username='root', password='WalletBackup2026!')

print("=== 创建已中奖和未中奖表 ===\n")

# 创建已中奖表
print("1. 创建 betting_records_won 表:")
stdin, stdout, stderr = ssh.exec_command("""mysql -uroot -p'WalletBackup2026!' wallet_backup -e "
CREATE TABLE IF NOT EXISTS betting_records_won (
    id INT AUTO_INCREMENT PRIMARY KEY,
    address VARCHAR(100) NOT NULL,
    match_id INT NOT NULL,
    match_name VARCHAR(255) NOT NULL,
    team_bet VARCHAR(100) NOT NULL,
    bet_amount DECIMAL(10,2) NOT NULL,
    odds DECIMAL(5,2) DEFAULT 2.00,
    potential_win DECIMAL(10,2),
    actual_win DECIMAL(10,2),
    settled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_address (address),
    INDEX idx_match_id (match_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"
""")
print(stdout.read().decode('utf-8'))
if stderr.read().decode('utf-8'):
    print("错误:", stderr.read().decode('utf-8'))

# 创建未中奖表
print("2. 创建 betting_records_lost 表:")
stdin, stdout, stderr = ssh.exec_command("""mysql -uroot -p'WalletBackup2026!' wallet_backup -e "
CREATE TABLE IF NOT EXISTS betting_records_lost (
    id INT AUTO_INCREMENT PRIMARY KEY,
    address VARCHAR(100) NOT NULL,
    match_id INT NOT NULL,
    match_name VARCHAR(255) NOT NULL,
    team_bet VARCHAR(100) NOT NULL,
    bet_amount DECIMAL(10,2) NOT NULL,
    odds DECIMAL(5,2) DEFAULT 2.00,
    settled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_address (address),
    INDEX idx_match_id (match_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"
""")
print(stdout.read().decode('utf-8'))
if stderr.read().decode('utf-8'):
    print("错误:", stderr.read().decode('utf-8'))

# 验证表结构
print("3. 验证表结构:")
stdin, stdout, stderr = ssh.exec_command("mysql -uroot -p'WalletBackup2026!' wallet_backup -e 'SHOW TABLES LIKE '\''betting%'\'';'")
print(stdout.read().decode('utf-8'))

ssh.close()
print("\n✅ 完成！")
