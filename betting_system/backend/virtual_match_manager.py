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
        
        # 缓存今日比赛到内存
        self.today_matches = []
        self.load_today_matches()
    
    def generate_daily_matches(self):
        """生成今日比赛 - 每个游戏24场，每小时3场（:00, :20, :40）"""
        today = date.today()
        now = datetime.now()
        games = ['lol', 'dota2', 'csgo']
        
        for game in games:
            # 获取该游戏未出场的队伍
            self.cursor.execute('''
                SELECT vt.id, vt.team_name FROM virtual_teams vt
                LEFT JOIN team_daily_matches tdm ON vt.id = tdm.team_id AND tdm.match_date = %s
                WHERE vt.game = %s AND tdm.id IS NULL
                ORDER BY RAND()
            ''', (today, game))
            
            available_teams = self.cursor.fetchall()
            
            if len(available_teams) < 72:
                print(f"{game} 可用队伍不足72支，跳过今日生成")
                continue
            
            # 取前72支队伍
            teams_to_match = available_teams[:72]
            
            # 随机打乱
            random.shuffle(teams_to_match)
            
            # 分成36对（24小时×3场/小时=72场，但只需要36对因为每对是一场比赛）
            match_index = 0
            for hour in range(now.hour, 24):  # 从当前小时开始
                for minute in [0, 20, 40]:  # 每小时的3个时间点
                    if match_index >= 36:  # 最多36场比赛
                        break
                    
                    if hour == now.hour and minute <= now.minute:
                        continue  # 跳过已经过去的时间点
                    
                    team_a = teams_to_match[match_index * 2]
                    team_b = teams_to_match[match_index * 2 + 1]
                    
                    # 随机决定哪队赢
                    winner = 'team_a' if random.random() < 0.5 else 'team_b'
                    
                    # 构建比赛时间
                    match_datetime = datetime(today.year, today.month, today.day, hour, minute, 0)
                    
                    # 插入比赛（包含winner字段）
                    self.cursor.execute('''
                        INSERT INTO virtual_matches (game, team_a_id, team_b_id, match_time, status, odds_a, odds_b, winner)
                        VALUES (%s, %s, %s, %s, 'pending', 2.00, 2.00, %s)
                    ''', (game, team_a['id'], team_b['id'], match_datetime, winner))
                    
                    match_id = self.cursor.lastrowid
                    
                    # 记录队伍今日出场
                    self.cursor.execute('''
                        INSERT INTO team_daily_matches (team_id, match_date, match_id)
                        VALUES (%s, %s, %s)
                    ''', (team_a['id'], today, match_id))
                    
                    self.cursor.execute('''
                        INSERT INTO team_daily_matches (team_id, match_date, match_id)
                        VALUES (%s, %s, %s)
                    ''', (team_b['id'], today, match_id))
                    
                    match_index += 1
            
            self.conn.commit()
            print(f"{game} 生成{match_index}场比赛完成")
        
        self.conn.commit()
        print(f"{today} 所有比赛生成完成！")
    
    def load_today_matches(self):
        """加载今日所有比赛到内存"""
        today = date.today()
        self.cursor.execute('''
            SELECT id, match_time, status FROM virtual_matches 
            WHERE DATE(match_time) = %s
        ''', (today,))
        self.today_matches = self.cursor.fetchall()
        print(f"已加载 {len(self.today_matches)} 场今日比赛到内存")
    
    def close_betting(self):
        """赛前2分钟关闭下注 - 固定时间:18、:38、:58"""
        now = datetime.now()
        
        # 只在:18、:38、:58执行
        if now.minute not in [18, 38, 58]:
            return
        
        # 直接更新所有pending的比赛为live，不查具体内容
        self.cursor.execute('''
            UPDATE virtual_matches 
            SET status = 'live'
            WHERE status = 'pending' AND DATE(match_time) = %s
        ''', (date.today(),))
        
        affected = self.cursor.rowcount
        self.conn.commit()
        
        if affected > 0:
            print(f"已关闭 {affected} 场比赛的下注")
    
    def settle_matches(self):
        """开奖前2分钟批量结算 - 从未结算表取出，删除，插入到已中奖/未中奖表"""
        two_minutes_later = datetime.now() + timedelta(minutes=2)
        
        # 1. 查询未结算表中，比赛将在2分钟后结束的订单
        self.cursor.execute('''
            SELECT br.id, br.address, br.match_id, br.match_name, br.team_bet, 
                   br.bet_amount, br.odds, br.potential_win,
                   vm.winner
            FROM betting_records br
            JOIN virtual_matches vm ON br.match_id = vm.id
            WHERE br.status = 'pending' AND vm.status = 'live' AND vm.match_time <= %s
        ''', (two_minutes_later,))
        
        pending_bets = self.cursor.fetchall()
        
        if not pending_bets:
            print("无需结算的订单")
            return
        
        won_count = 0
        lost_count = 0
        
        # 2. 逐条处理：删除未结算记录，插入到对应表
        for bet in pending_bets:
            bet_id = bet['id']
            winner = bet['winner']
            is_won = (bet['team_bet'] == winner)
            
            if is_won:
                # 已中奖：插入到 betting_records_won
                actual_win = float(bet['bet_amount']) * float(bet['odds'])
                self.cursor.execute('''
                    INSERT INTO betting_records_won 
                    (address, match_id, match_name, team_bet, bet_amount, odds, potential_win, actual_win)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    bet['address'], bet['match_id'], bet['match_name'],
                    bet['team_bet'], bet['bet_amount'], bet['odds'],
                    bet['potential_win'], actual_win
                ))
                
                # 发放奖励到用户积分
                self.cursor.execute('''
                    UPDATE user_points SET points = points + %s WHERE address = %s
                ''', (actual_win, bet['address']))
                
                won_count += 1
            else:
                # 未中奖：插入到 betting_records_lost
                self.cursor.execute('''
                    INSERT INTO betting_records_lost 
                    (address, match_id, match_name, team_bet, bet_amount, odds)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (
                    bet['address'], bet['match_id'], bet['match_name'],
                    bet['team_bet'], bet['bet_amount'], bet['odds']
                ))
                
                lost_count += 1
            
            # 3. 从未结算表中删除
            self.cursor.execute('''
                DELETE FROM betting_records WHERE id = %s
            ''', (bet_id,))
        
        self.conn.commit()
        print(f"批量结算完成: {won_count} 个已中奖, {lost_count} 个未中奖")
    
    def close(self):
        self.conn.close()


def main():
    """主循环 - 每1分钟检查一次"""
    manager = VirtualMatchManager()
    
    print("虚拟赛事自动管理系统启动")
    print("功能：自动生成比赛、关闭下注、自动结算")
    
    last_generate_date = None  # 记录上次生成的日期
    
    while True:
        try:
            now = datetime.now()
            
            # 每分钟检查关闭下注（赛前2分钟）
            manager.close_betting()
            
            # 在18:10、38:10、58:10执行结算
            if now.second == 10 and now.minute in [18, 38, 58]:
                manager.settle_matches()
            
            time.sleep(60)  # 1分钟
            
        except KeyboardInterrupt:
            print("\n程序退出")
            manager.close()
            break
        except Exception as e:
            print(f"错误: {e}")
            time.sleep(60)


if __name__ == '__main__':
    main()
