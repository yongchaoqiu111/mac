"""虚拟赛事自动管理系统 - 自动生成比赛、裁判、结算"""
import pymysql
import random
from datetime import datetime, timedelta, date
import os
import time

# 数据库配置
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'WalletBackup2026!'),
    'database': os.environ.get('DB_NAME', 'wallet_backup'),
    'charset': 'utf8mb4'
}

class VirtualMatchManager:
    def __init__(self):
        self.conn = pymysql.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
    
    def generate_daily_matches(self):
        """生成今日比赛 - 24小时×3场=72场，每小时3个游戏各1场"""
        today = date.today()
        games = ['lol', 'dota2', 'csgo']
        
        # 生成24小时时间段
        all_time_slots = []
        for hour in range(24):
            all_time_slots.append(f"{hour:02d}:00")
        
        print(f"生成{len(all_time_slots)}个时间段（24小时）")
        
        # 为每个游戏准备48支队伍（24小时×1场×2队=48队）
        game_teams = {}
        for game in games:
            self.cursor.execute('''
                SELECT vt.id, vt.team_name FROM virtual_teams vt
                LEFT JOIN team_daily_matches tdm ON vt.id = tdm.team_id AND tdm.match_date = %s
                WHERE vt.game = %s AND tdm.id IS NULL
                ORDER BY RAND()
            ''', (today, game))
            
            available_teams = self.cursor.fetchall()
            
            if len(available_teams) < 48:
                print(f"{game} 可用队伍不足48支，跳过今日生成")
                return
            
            teams = available_teams[:48]
            random.shuffle(teams)
            game_teams[game] = teams
        
        # 生成比赛：每小时3场（:00、:20、:40各1场）
        match_count = 0
        for hour in range(24):
            # 每个小时内的3个时间段
            minutes = [0, 20, 40]
            
            # 随机打乱3个游戏的顺序
            shuffled_games = games.copy()
            random.shuffle(shuffled_games)
            
            # 为每个游戏生成1场比赛，分别在不同分钟
            for i, game in enumerate(shuffled_games):
                teams = game_teams[game]
                minute = minutes[i]  # 0、20、40
                time_slot = f"{hour:02d}:{minute:02d}"
                
                if len(teams) >= 2:
                    team_a = teams.pop(0)
                    team_b = teams.pop(0)
                    
                    match_datetime = datetime.strptime(f"{today} {time_slot}", '%Y-%m-%d %H:%M')
                    
                    self.cursor.execute('''
                        INSERT INTO virtual_matches (game, team_a_id, team_b_id, match_time, status, odds_a, odds_b)
                        VALUES (%s, %s, %s, %s, 'pending', 2.00, 2.00)
                    ''', (game, team_a['id'], team_b['id'], match_datetime))
                    
                    match_id = self.cursor.lastrowid
                    
                    self.cursor.execute('''
                        INSERT INTO team_daily_matches (team_id, match_date, match_id)
                        VALUES (%s, %s, %s)
                    ''', (team_a['id'], today, match_id))
                    
                    self.cursor.execute('''
                        INSERT INTO team_daily_matches (team_id, match_date, match_id)
                        VALUES (%s, %s, %s)
                    ''', (team_b['id'], today, match_id))
                    
                    match_count += 1
        
        self.conn.commit()
        print(f"成功生成{match_count}场比赛（24小时×3场）")
    
    def close_betting(self):
        """赛前2分钟关闭下注 - 将pending转为live"""
        now = datetime.now()
        two_minutes_later = now + timedelta(minutes=2)
        
        self.cursor.execute('''
            UPDATE virtual_matches 
            SET status = 'live'
            WHERE status = 'pending' AND match_time <= %s
        ''', (two_minutes_later,))
        
        affected = self.cursor.rowcount
        self.conn.commit()
        
        if affected > 0:
            print(f"已关闭 {affected} 场比赛的下注")
    
    def settle_matches(self):
        """比赛1小时后自动结算"""
        one_hour_ago = datetime.now() - timedelta(hours=1)
        
        self.cursor.execute('''
            SELECT vm.id, vm.team_a_id, vm.team_b_id, vm.game,
                   br.id as bet_id, br.address, br.bet_amount, br.team_bet, br.odds
            FROM virtual_matches vm
            LEFT JOIN betting_records br ON vm.id = br.match_id
            WHERE vm.status = 'live' AND vm.match_time <= %s
        ''', (one_hour_ago,))
        
        matches = self.cursor.fetchall()
        
        if not matches:
            print("无需结算的比赛")
            return
        
        # 按比赛分组
        match_dict = {}
        for row in matches:
            match_id = row['id']
            if match_id not in match_dict:
                match_dict[match_id] = {
                    'team_a_id': row['team_a_id'],
                    'team_b_id': row['team_b_id'],
                    'game': row['game'],
                    'bets': []
                }
            if row['bet_id']:
                match_dict[match_id]['bets'].append({
                    'bet_id': row['bet_id'],
                    'address': row['address'],
                    'bet_amount': float(row['bet_amount']),
                    'team_bet': row['team_bet'],
                    'odds': float(row['odds'])
                })
        
        # 随机判定胜负并结算
        for match_id, match_data in match_dict.items():
            winner = random.choice(['team_a', 'team_b'])
            
            self.cursor.execute('''
                UPDATE virtual_matches SET status = 'finished', winner = %s WHERE id = %s
            ''', (winner, match_id))
            
            for bet in match_data['bets']:
                bet_won = (bet['team_bet'] == winner)
                win_amount = bet['bet_amount'] * bet['odds'] if bet_won else 0
                
                if bet_won:
                    self.cursor.execute('''
                        UPDATE user_points SET points = points + %s WHERE address = %s
                    ''', (win_amount, bet['address']))
                    
                    self.cursor.execute('''
                        UPDATE betting_records 
                        SET status = 'won', win_amount = %s, updated_at = NOW()
                        WHERE id = %s
                    ''', (win_amount, bet['bet_id']))
                    
                    self.cursor.execute('''
                        INSERT INTO points_transactions (address, transaction_type, amount, balance_after, description, related_id)
                        VALUES (%s, 'bet_win', %s, NULL, %s, %s)
                    ''', (bet['address'], win_amount, f'竞猜中奖: 比赛{match_id}', bet['bet_id']))
                else:
                    self.cursor.execute('''
                        UPDATE betting_records 
                        SET status = 'lost', win_amount = 0, updated_at = NOW()
                        WHERE id = %s
                    ''', (bet['bet_id']))
            
            print(f"比赛 {match_id} 结算完成，获胜方: {winner}")
        
        self.conn.commit()
        print(f"共结算 {len(match_dict)} 场比赛")
    
    def close(self):
        self.conn.close()


def main():
    """主循环 - 每5分钟检查一次"""
    manager = VirtualMatchManager()
    
    print("虚拟赛事自动管理系统启动")
    print("功能：自动生成比赛、关闭下注、自动结算")
    
    last_generate_date = None
    
    while True:
        try:
            now = datetime.now()
            today = now.date()
            
            # 每天 00:00-00:05 之间生成今日比赛
            if now.hour == 0 and now.minute < 5 and last_generate_date != today:
                print(f"\n[{now}] 生成今日比赛...")
                manager.generate_daily_matches()
                last_generate_date = today
            
            # 每5分钟检查关闭下注
            if now.minute % 5 == 0:
                manager.close_betting()
            
            # 每5分钟检查结算
            if now.minute % 5 == 0:
                manager.settle_matches()
            
            time.sleep(300)
            
        except KeyboardInterrupt:
            print("\n程序退出")
            manager.close()
            break
        except Exception as e:
            print(f"错误: {e}")
            time.sleep(60)


if __name__ == '__main__':
    main()
