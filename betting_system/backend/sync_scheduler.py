"""定时同步赛事数据"""
import schedule
import time
import requests
import pymysql
import os

# 数据库配置（与routes.py一致）
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'WalletBackup2026!'),
    'database': os.environ.get('DB_NAME', 'wallet_backup'),
    'charset': 'utf8mb4'
}

PANDASCORE_API_KEY = "7SU7xFYhMi2z3Otlw89M1x53Ln4b10qWBiZQmY6bz86QgQ7Gf0Q"
PANDASCORE_BASE_URL = "https://api.pandascore.co"

def sync_game(game):
    """同步单个游戏的赛事数据"""
    try:
        url = f"{PANDASCORE_BASE_URL}/matches/upcoming"
        headers = {'Authorization': f'Bearer {PANDASCORE_API_KEY}'}
        params = {'filter[videogame]': game, 'page': 1, 'per_page': 50}
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code != 200:
            print(f"[{game.upper()}] API请求失败: {response.status_code}")
            return 0
        
        matches_data = response.json()
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        synced = 0
        for match in matches_data:
            match_id = match.get('id')
            if not match_id:
                continue
            
            # 检查是否已存在
            cursor.execute('SELECT id FROM matches WHERE pandascore_id = %s', (str(match_id),))
            if cursor.fetchone():
                continue
            
            # 提取数据
            teams = match.get('opponents', [])
            team1 = teams[0].get('opponent', {}).get('name', '未知') if len(teams) > 0 else '未知'
            team2 = teams[1].get('opponent', {}).get('name', '未知') if len(teams) > 1 else '未知'
            
            league = match.get('league', {})
            league_name = league.get('name', None) if league else None
            
            begin_at = match.get('begin_at')
            
            cursor.execute(
                'INSERT INTO matches (pandascore_id, game, team1, team2, league_name, start_time, status, odds_team1, odds_team2) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                (str(match_id), game, team1, team2, league_name, begin_at, 'upcoming', 2.0, 2.0)
            )
            synced += 1
        
        conn.commit()
        conn.close()
        print(f"[{game.upper()}] 同步完成: {synced} 场")
        return synced
        
    except Exception as e:
        print(f"[{game.upper()}] 错误: {e}")
        return 0

def sync_all():
    """同步所有游戏"""
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] 开始同步赛事数据...")
    total = 0
    for game in ['lol', 'dota2', 'csgo']:
        total += sync_game(game)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 总计同步: {total} 场\n")

if __name__ == '__main__':
    # 立即执行一次
    sync_all()
    
    # 每6小时同步一次
    schedule.every(6).hours.do(sync_all)
    
    print("定时任务已启动，每6小时同步一次")
    while True:
        schedule.run_pending()
        time.sleep(60)
