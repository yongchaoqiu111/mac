"""创建虚拟赛事系统数据库表"""
import pymysql
import os

# 数据库配置
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'WalletBackup2026!'),
    'database': os.environ.get('DB_NAME', 'wallet_backup'),
    'charset': 'utf8mb4'
}

def create_tables():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 1. 创建队伍表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS virtual_teams (
            id INT AUTO_INCREMENT PRIMARY KEY,
            game ENUM('lol', 'dota2', 'csgo') NOT NULL,
            team_name VARCHAR(100) NOT NULL,
            logo_url VARCHAR(255) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_team (game, team_name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ''')
    
    # 2. 创建比赛表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS virtual_matches (
            id INT AUTO_INCREMENT PRIMARY KEY,
            game ENUM('lol', 'dota2', 'csgo') NOT NULL,
            team_a_id INT NOT NULL,
            team_b_id INT NOT NULL,
            match_time DATETIME NOT NULL COMMENT '比赛开始时间',
            status ENUM('pending', 'live', 'finished') DEFAULT 'pending',
            winner ENUM('team_a', 'team_b') DEFAULT NULL COMMENT '获胜方',
            odds_a DECIMAL(5,2) DEFAULT 2.00,
            odds_b DECIMAL(5,2) DEFAULT 2.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_a_id) REFERENCES virtual_teams(id),
            FOREIGN KEY (team_b_id) REFERENCES virtual_teams(id),
            INDEX idx_match_time (match_time),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ''')
    
    # 3. 创建队伍每日出场记录表（确保每队每天只打1场）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_daily_matches (
            id INT AUTO_INCREMENT PRIMARY KEY,
            team_id INT NOT NULL,
            match_date DATE NOT NULL,
            match_id INT NOT NULL,
            UNIQUE KEY unique_team_daily (team_id, match_date),
            FOREIGN KEY (team_id) REFERENCES virtual_teams(id),
            FOREIGN KEY (match_id) REFERENCES virtual_matches(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ''')
    
    conn.commit()
    conn.close()
    print("数据库表创建成功！")

if __name__ == '__main__':
    create_tables()
