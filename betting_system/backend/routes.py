"""
竞猜系统后端API服务
端口: 5004
功能: 积分管理、竞猜下注、积分兑换
独立模块，可单独部署
"""
from flask import Flask, Blueprint, jsonify, request
from flask_cors import CORS
import pymysql
import os
import time
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # 允许所有跨域请求
betting_bp = Blueprint('betting', __name__, url_prefix='/betting')

# 数据库配置
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'WalletBackup2026!'),
    'database': os.environ.get('DB_NAME', 'wallet_backup'),
    'charset': 'utf8mb4'
}

# PandaScore API配置
PANDASCORE_API_KEY = os.environ.get('PANDASCORE_API_KEY', '7SU7xFYhMi2z3Otlw89M1x53Ln4b10qWBiZQmY6bz86QgQ7Gf0Q')
PANDASCORE_BASE_URL = "https://api.pandascore.co"


def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)


# ==================== 积分管理 ====================

@betting_bp.route('/points/balance', methods=['POST'])
def get_points_balance():
    """查询用户积分余额"""
    try:
        data = request.get_json(force=True)
        address = data.get('address')
        
        if not address:
            return jsonify({'success': False, 'message': '缺少address参数'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute('SELECT points, total_earned, total_spent FROM user_points WHERE address = %s', (address,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return jsonify({
                'success': True,
                'points': float(result['points']),
                'total_earned': float(result['total_earned']),
                'total_spent': float(result['total_spent'])
            }), 200
        else:
            return jsonify({
                'success': True,
                'points': 0.0,
                'total_earned': 0.0,
                'total_spent': 0.0
            }), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@betting_bp.route('/points/convert', methods=['POST'])
def convert_usdt_to_points():
    """USDT余额转换为积分 (1 USDT = 1 积分)"""
    try:
        data = request.get_json(force=True)
        address = data.get('address')
        usdt_amount = float(data.get('usdt_amount', 0))
        
        if not address or usdt_amount <= 0:
            return jsonify({'success': False, 'message': '参数错误'}), 400
        
        points_to_add = usdt_amount
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT points FROM user_points WHERE address = %s', (address,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute(
                    'UPDATE user_points SET points = points + %s, total_earned = total_earned + %s WHERE address = %s',
                    (points_to_add, points_to_add, address)
                )
                new_balance = existing[0] + points_to_add
            else:
                cursor.execute(
                    'INSERT INTO user_points (address, points, total_earned) VALUES (%s, %s, %s)',
                    (address, points_to_add, points_to_add)
                )
                new_balance = points_to_add
            
            cursor.execute(
                'INSERT INTO points_transactions (address, transaction_type, amount, balance_after, description) VALUES (%s, %s, %s, %s, %s)',
                (address, 'convert', points_to_add, new_balance, f'USDT转换积分: {usdt_amount} USDT')
            )
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'points_added': points_to_add,
                'new_balance': new_balance,
                'message': f'成功转换 {usdt_amount} USDT 为 {points_to_add} 积分'
            }), 200
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 赛事数据板块 ====================

@betting_bp.route('/matches/list', methods=['POST'])
def get_matches_list():
    """获取赛事列表（查询最近2小时的比赛）"""
    try:
        data = request.get_json(force=True)
        game = data.get('game', 'all')  # all, lol, dota2, csgo
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 查询今日未开始的比赛（pending状态且match_time > 当前时间）
        from datetime import date, datetime
        today = date.today()
        now = datetime.now()
        
        if game == 'all':
            cursor.execute('''
                SELECT vm.id, vm.game, vt1.team_name as team1, vt2.team_name as team2,
                       vm.match_time, vm.status, vm.odds_a, vm.odds_b,
                       DATE_FORMAT(vm.match_time, '%%Y-%%m-%%dT%%H:%%i:%%s') as start_time
                FROM virtual_matches vm
                JOIN virtual_teams vt1 ON vm.team_a_id = vt1.id
                JOIN virtual_teams vt2 ON vm.team_b_id = vt2.id
                WHERE DATE(vm.match_time) = %s AND vm.status = 'pending' AND vm.match_time > %s
                ORDER BY vm.match_time
            ''', (today, now))
        else:
            cursor.execute('''
                SELECT vm.id, vm.game, vt1.team_name as team1, vt2.team_name as team2,
                       vm.match_time, vm.status, vm.odds_a, vm.odds_b,
                       DATE_FORMAT(vm.match_time, '%%Y-%%m-%%dT%%H:%%i:%%s') as start_time
                FROM virtual_matches vm
                JOIN virtual_teams vt1 ON vm.team_a_id = vt1.id
                JOIN virtual_teams vt2 ON vm.team_b_id = vt2.id
                WHERE vm.game = %s AND DATE(vm.match_time) = %s AND vm.status = 'pending' AND vm.match_time > %s
                ORDER BY vm.match_time
            ''', (game, today, now))
        
        matches = cursor.fetchall()
        conn.close()
        
        # 转换格式
        for match in matches:
            match['pandascore_id'] = match['id']
            match['league_name'] = 'Virtual League'
            match['odds_team1'] = float(match['odds_a'])
            match['odds_team2'] = float(match['odds_b'])
            match['odds_a'] = float(match['odds_a'])
            match['odds_b'] = float(match['odds_b'])
            if match['match_time']:
                match['match_time'] = match['match_time'].strftime('%Y-%m-%dT%H:%M:%S')
        
        return jsonify({
            'success': True,
            'matches': matches,
            'total': len(matches)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@betting_bp.route('/matches/detail', methods=['POST'])
def get_match_detail():
    """获取赛事详情和赔率"""
    try:
        data = request.get_json(force=True)
        match_id = int(data.get('match_id'))
        
        if not match_id:
            return jsonify({'success': False, 'message': '缺少match_id参数'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute('SELECT * FROM matches WHERE id = %s', (match_id,))
        match = cursor.fetchone()
        conn.close()
        
        if not match:
            return jsonify({'success': False, 'message': '赛事不存在'}), 404
        
        for key in ['odds_team1', 'odds_team2']:
            if match[key] is not None:
                match[key] = float(match[key])
        
        return jsonify({
            'success': True,
            'match': match
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@betting_bp.route('/matches/sync', methods=['POST'])
def sync_matches_from_pandascore():
    """从PandaScore同步赛事数据（定时任务调用）"""
    try:
        data = request.get_json(force=True)
        game = data.get('game', 'lol')
        
        url = f"{PANDASCORE_BASE_URL}/matches/upcoming"
        headers = {'Authorization': f'Bearer {PANDASCORE_API_KEY}'}
        params = {'filter[videogame]': game, 'page': 1, 'per_page': 50}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            return jsonify({'success': False, 'message': 'PandaScore API请求失败'}), 500
        
        matches_data = response.json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        synced_count = 0
        for match in matches_data:
            match_id = match.get('id')
            if not match_id:
                continue
            
            # 检查是否已存在
            cursor.execute('SELECT id FROM matches WHERE pandascore_id = %s', (match_id,))
            if cursor.fetchone():
                continue
            
            # 插入新赛事
            teams = match.get('opponents', [])
            team1 = teams[0].get('opponent', {}).get('name', '未知') if len(teams) > 0 else '未知'
            team2 = teams[1].get('opponent', {}).get('name', '未知') if len(teams) > 1 else '未知'
            
            # 提取联赛名称
            league = match.get('league', {})
            league_name = league.get('name', None) if league else None
            
            begin_at = match.get('begin_at')
            if begin_at:
                from datetime import datetime
                begin_at = datetime.fromisoformat(begin_at.replace('Z', '+00:00'))
            
            cursor.execute(
                'INSERT INTO matches (pandascore_id, game, team1, team2, league_name, start_time, status, odds_team1, odds_team2) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                (match_id, game, team1, team2, league_name, begin_at, 'upcoming', 2.0, 2.0)
            )
            synced_count += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'synced_count': synced_count,
            'message': f'成功同步 {synced_count} 场赛事'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 参与竞猜板块 ====================

@betting_bp.route('/bet/place', methods=['POST'])
def place_bet():
    """下注竞猜"""
    try:
        data = request.get_json(force=True)
        address = data.get('address')
        match_id = int(data.get('match_id'))
        match_name = data.get('match_name')
        team_bet = data.get('team_bet')
        bet_amount = float(data.get('bet_amount'))
        odds = float(data.get('odds', 2.0))
        
        if not all([address, match_id, team_bet, bet_amount]):
            return jsonify({'success': False, 'message': '参数不完整'}), 400
        
        if bet_amount <= 0:
            return jsonify({'success': False, 'message': '下注金额必须大于0'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        try:
            # 1. 检查比赛状态 - 必须是pending状态才能下注
            cursor.execute('SELECT status, match_time FROM virtual_matches WHERE id = %s', (match_id,))
            match = cursor.fetchone()
            
            if not match:
                return jsonify({'success': False, 'message': '比赛不存在'}), 404
            
            if match['status'] == 'live':
                return jsonify({'success': False, 'message': '比赛已开始，无法下注'}), 400
            
            if match['status'] == 'finished':
                return jsonify({'success': False, 'message': '比赛已结束，无法下注'}), 400
            
            # 检查是否在全局封盘时间段（每小时的18-19、38-39、58-59分，共2分钟）
            from datetime import datetime
            now = datetime.now()
            
            if (now.minute == 18 or now.minute == 19) or \
               (now.minute == 38 or now.minute == 39) or \
               (now.minute == 58 or now.minute == 59):
                return jsonify({'success': False, 'message': '当前为封盘时间，无法下注'}), 400
            
            # 2. 检查用户积分
            cursor.execute('SELECT points FROM user_points WHERE address = %s', (address,))
            user = cursor.fetchone()
            
            if not user or user['points'] < bet_amount:
                return jsonify({'success': False, 'message': '积分余额不足'}), 400
            
            # 将Decimal转换为float
            user_points = float(user['points'])
            new_balance = user_points - bet_amount
            cursor.execute(
                'UPDATE user_points SET points = %s, total_spent = total_spent + %s WHERE address = %s',
                (new_balance, bet_amount, address)
            )
            
            potential_win = bet_amount * odds
            cursor.execute(
                'INSERT INTO betting_records (address, match_id, match_name, team_bet, bet_amount, odds, potential_win) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (address, match_id, match_name, team_bet, bet_amount, odds, potential_win)
            )
            bet_id = cursor.lastrowid
            
            cursor.execute(
                'INSERT INTO points_transactions (address, transaction_type, amount, balance_after, description, related_id) VALUES (%s, %s, %s, %s, %s, %s)',
                (address, 'bet', -bet_amount, new_balance, f'竞猜下注: {match_name}', bet_id)
            )
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'bet_id': bet_id,
                'bet_amount': bet_amount,
                'new_balance': new_balance,
                'potential_win': potential_win,
                'message': '下注成功'
            }), 200
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@betting_bp.route('/bet/settle', methods=['POST'])
def settle_bet():
    """结算竞猜（由管理员或自动触发）"""
    try:
        data = request.get_json(force=True)
        bet_id = int(data.get('bet_id'))
        is_win = data.get('is_win', False)  # True=赢，False=输
        actual_win = float(data.get('actual_win', 0))
        
        if not bet_id:
            return jsonify({'success': False, 'message': '缺少bet_id参数'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        try:
            # 查询下注记录
            cursor.execute('SELECT * FROM betting_records WHERE id = %s AND status = \'pending\'', (bet_id,))
            bet_record = cursor.fetchone()
            
            if not bet_record:
                return jsonify({'success': False, 'message': '下注记录不存在或已结算'}), 404
            
            address = bet_record['address']
            bet_amount = float(bet_record['bet_amount'])
            
            if is_win:
                # 竞猜赢了，发放奖励
                cursor.execute(
                    'UPDATE user_points SET points = points + %s, total_earned = total_earned + %s WHERE address = %s',
                    (actual_win, actual_win, address)
                )
                
                cursor.execute(
                    'SELECT points FROM user_points WHERE address = %s',
                    (address,)
                )
                new_balance = cursor.fetchone()['points']
                
                cursor.execute(
                    'INSERT INTO points_transactions (address, transaction_type, amount, balance_after, description, related_id) VALUES (%s, %s, %s, %s, %s, %s)',
                    (address, 'win', actual_win, new_balance, f'竞猜奖励: {bet_record["match_name"]}', bet_id)
                )
                
                cursor.execute(
                    'UPDATE betting_records SET status = \'won\', actual_win = %s WHERE id = %s',
                    (actual_win, bet_id)
                )
                
                message = f'恭喜！竞猜赢了，获得 {actual_win} 积分奖励'
            else:
                # 竞猜输了，已在下注时扣除了积分，只需更新状态
                cursor.execute(
                    'UPDATE betting_records SET status = \'lost\', actual_win = 0 WHERE id = %s',
                    (bet_id,)
                )
                
                cursor.execute(
                    'SELECT points FROM user_points WHERE address = %s',
                    (address,)
                )
                new_balance = cursor.fetchone()['points']
                
                # 可选：添加输奖记录（便于统计）
                cursor.execute(
                    'INSERT INTO points_transactions (address, transaction_type, amount, balance_after, description, related_id) VALUES (%s, %s, %s, %s, %s, %s)',
                    (address, 'loss', 0, new_balance, f'竞猜未中: {bet_record["match_name"]}', bet_id)
                )
                
                message = '很遗憾，竞猜未中'
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'bet_id': bet_id,
                'is_win': is_win,
                'actual_win': actual_win if is_win else 0,
                'message': message
            }), 200
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@betting_bp.route('/bet/my-bets', methods=['POST'])
def get_my_bets():
    """查询我的竞猜记录"""
    try:
        data = request.get_json(force=True)
        address = data.get('address')
        status = data.get('status', 'all')  # all, pending, won, lost
        
        if not address:
            return jsonify({'success': False, 'message': '缺少address参数'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        query = 'SELECT * FROM betting_records WHERE address = %s'
        params = [address]
        
        if status != 'all':
            query += ' AND status = %s'
            params.append(status)
        
        query += ' ORDER BY created_at DESC LIMIT 50'
        
        cursor.execute(query, params)
        records = cursor.fetchall()
        conn.close()
        
        for record in records:
            for key in ['bet_amount', 'odds', 'potential_win', 'actual_win']:
                if record[key] is not None:
                    record[key] = float(record[key])
        
        return jsonify({
            'success': True,
            'records': records,
            'count': len(records)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 兑换系统 ====================

@betting_bp.route('/exchange/request', methods=['POST'])
def request_exchange():
    """申请积分兑换USDT"""
    try:
        data = request.get_json(force=True)
        address = data.get('address')
        points_amount = float(data.get('points_amount'))
        usdt_amount = float(data.get('usdt_amount'))
        exchange_rate = float(data.get('exchange_rate', 1.0))
        
        if not address or points_amount <= 0 or usdt_amount <= 0:
            return jsonify({'success': False, 'message': '参数错误'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute('SELECT points FROM user_points WHERE address = %s', (address,))
            user = cursor.fetchone()
            
            if not user or user['points'] < points_amount:
                return jsonify({'success': False, 'message': '积分余额不足'}), 400
            
            order_no = f"EX{int(time.time())}{address[-6:]}"
            
            cursor.execute(
                'INSERT INTO exchange_orders (order_no, address, points_amount, usdt_amount, exchange_rate) VALUES (%s, %s, %s, %s, %s)',
                (order_no, address, points_amount, usdt_amount, exchange_rate)
            )
            order_id = cursor.lastrowid
            
            new_balance = user['points'] - points_amount
            cursor.execute(
                'UPDATE user_points SET points = %s, total_spent = total_spent + %s WHERE address = %s',
                (new_balance, points_amount, address)
            )
            
            cursor.execute(
                'INSERT INTO points_transactions (address, transaction_type, amount, balance_after, description, related_id) VALUES (%s, %s, %s, %s, %s, %s)',
                (address, 'exchange', -points_amount, new_balance, f'申请兑换USDT: {usdt_amount}', order_id)
            )
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'order_no': order_no,
                'order_id': order_id,
                'points_deducted': points_amount,
                'usdt_amount': usdt_amount,
                'new_balance': new_balance,
                'message': '兑换申请已提交，等待后台审核'
            }), 200
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@betting_bp.route('/exchange/history', methods=['POST'])
def get_exchange_history():
    """查询兑换历史"""
    try:
        data = request.get_json(force=True)
        address = data.get('address')
        
        if not address:
            return jsonify({'success': False, 'message': '缺少address参数'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute(
            'SELECT * FROM exchange_orders WHERE address = %s ORDER BY created_at DESC LIMIT 50',
            (address,)
        )
        orders = cursor.fetchall()
        conn.close()
        
        for order in orders:
            for key in ['points_amount', 'usdt_amount', 'exchange_rate']:
                if order[key] is not None:
                    order[key] = float(order[key])
        
        return jsonify({
            'success': True,
            'orders': orders,
            'count': len(orders)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== TRX兑换系统 ====================

@betting_bp.route('/debt/check', methods=['POST'])
def check_debt():
    """检查用户是否有未付清的欠款"""
    try:
        data = request.get_json(force=True)
        address = data.get('address')
        
        if not address:
            return jsonify({'success': False, 'message': '缺少address参数'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute('''
            SELECT id, debt_amount, paid_amount, (debt_amount - paid_amount) as remaining 
            FROM user_debts 
            WHERE address = %s AND status = 0
            ORDER BY created_at DESC LIMIT 1
        ''', (address,))
        
        debt = cursor.fetchone()
        conn.close()
        
        if debt:
            return jsonify({
                'success': True,
                'has_debt': True,
                'debt': {
                    'id': debt['id'],
                    'debt_amount': float(debt['debt_amount']),
                    'paid_amount': float(debt['paid_amount']),
                    'remaining': float(debt['remaining']),
                    'pay_amount': float(debt['debt_amount']),  # 应付金额
                    'receive_address': 'TBo93T5a1iP31rdFF8aeowaDvrhxVbCjac'
                }
            }), 200
        else:
            return jsonify({
                'success': True,
                'has_debt': False
            }), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@betting_bp.route('/exchange/cooldown', methods=['POST'])
def check_exchange_cooldown():
    """检查24小时兑换冷却时间"""
    try:
        data = request.get_json(force=True)
        address = data.get('address')
        
        if not address:
            return jsonify({'success': False, 'message': '缺少address参数'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute('''
            SELECT last_exchange_time 
            FROM user_points 
            WHERE address = %s
        ''', (address,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result['last_exchange_time']:
            last_time = result['last_exchange_time']
            now = time.time()
            last_timestamp = last_time.timestamp()
            elapsed = now - last_timestamp
            
            if elapsed < 86400:  # 24小时 = 86400秒
                remaining = 86400 - elapsed
                hours = int(remaining // 3600)
                minutes = int((remaining % 3600) // 60)
                next_time = last_time.replace(hour=last_time.hour + hours, minute=last_time.minute + minutes)
                
                return jsonify({
                    'success': True,
                    'can_exchange': False,
                    'remaining_seconds': int(remaining),
                    'next_time': next_time.strftime('%Y-%m-%d %H:%M:%S')
                }), 200
        
        return jsonify({
            'success': True,
            'can_exchange': True
        }), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@betting_bp.route('/exchange/to_trx', methods=['POST'])
def exchange_to_trx():
    """积分兑换TRX：查询链上TRX余额，1:1兑换"""
    try:
        data = request.get_json(force=True)
        address = data.get('address')
        points_amount = float(data.get('points_amount', 0))
        
        if not address:
            return jsonify({'success': False, 'message': '参数错误'}), 400
        
        # 步1：检查24小时限制
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute('SELECT last_exchange_time FROM user_points WHERE address = %s', (address,))
        user = cursor.fetchone()
        
        if user and user['last_exchange_time']:
            from datetime import timedelta
            last_exchange = user['last_exchange_time']
            time_diff = datetime.now() - last_exchange
            
            if time_diff < timedelta(hours=24):
                hours_left = 24 - (time_diff.total_seconds() / 3600)
                conn.close()
                return jsonify({
                    'success': False,
                    'message': f'24小时内只能兑换一次，请{hours_left:.1f}小时后再试'
                }), 400
        
        # 步2：查询TRON链上余额
        tron_balance = get_tron_balance(address)
                
        if tron_balance <= 0:
            conn.close()
            return jsonify({
                'success': False, 
                'message': '钱包TRX余额为0，请先充值'
            }), 400
                
        # 如果points_amount为0，则兑换全部余额
        if points_amount == 0:
            points_amount = tron_balance
        elif points_amount > tron_balance:
            conn.close()
            return jsonify({
                'success': False, 
                'message': f'TRX余额不足，当前余额: {tron_balance} TRX，需要: {points_amount} TRX'
            }), 400
                
        # 步3：检查用户是否有积分记录
        cursor.execute('SELECT points FROM user_points WHERE address = %s', (address,))
        user = cursor.fetchone()
        
        if not user:
            # 创建用户积分记录
            cursor.execute(
                'INSERT INTO user_points (address, points, total_earned) VALUES (%s, %s, %s)',
                (address, points_amount, points_amount)
            )
        else:
            # 更新积分（不是叠加！）
            cursor.execute(
                'UPDATE user_points SET points = %s, total_earned = total_earned + %s, last_exchange_time = NOW() WHERE address = %s',
                (points_amount, points_amount, address)
            )
        
        # 记录流水
        cursor.execute(
            'INSERT INTO points_transactions (address, transaction_type, amount, balance_after, description) VALUES (%s, %s, %s, %s, %s)',
            (address, 'exchange', points_amount, points_amount, f'TRX兑换积分: {points_amount}')
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'trx_amount': points_amount,
            'message': f'成功兑换 {points_amount} 积分'
        }), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


def get_tron_balance(address):
    """查询TRON地址的TRX余额"""
    try:
        # 使用TronGrid API查询余额
        url = f"https://api.trongrid.io/v1/accounts/{address}"
        headers = {
            "TRON-PRO-API-KEY": "4858ecc5-60f2-4e06-a1a1-2aa35be108ac"
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            balance_sun = data.get('data', [{}])[0].get('balance', 0)
            # 1 TRX = 1,000,000 SUN
            return balance_sun / 1000000
        else:
            return 0.0
    except:
        return 0.0


@betting_bp.route('/debt/payment_status', methods=['POST'])
def check_debt_payment_status():
    """检查欠款支付状态"""
    try:
        data = request.get_json(force=True)
        debt_id = data.get('debt_id')
        
        if not debt_id:
            return jsonify({'success': False, 'message': '缺少debt_id参数'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute('SELECT status FROM user_debts WHERE id = %s', (debt_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return jsonify({
                'success': True,
                'paid': result['status'] == 1
            }), 200
        else:
            return jsonify({'success': False, 'message': '订单不存在'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== PandaScore对接 ====================

@betting_bp.route('/api/pandascore/matches', methods=['GET'])
def get_upcoming_matches():
    """获取即将开始的比赛"""
    try:
        game = request.args.get('game', 'lol')
        page = request.args.get('page', 1)
        
        url = f"{PANDASCORE_BASE_URL}/matches/upcoming"
        headers = {'Authorization': f'Bearer {PANDASCORE_API_KEY}'}
        params = {'filter[videogame]': game, 'page': page, 'per_page': 20}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'matches': response.json()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'PandaScore API请求失败'
            }), response.status_code
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# 注册蓝图
app.register_blueprint(betting_bp)

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=5004, debug=False)
