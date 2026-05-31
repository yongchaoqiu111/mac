"""
积分与竞猜API服务
端口: 5004
功能: 积分管理、竞猜下注、积分兑换
"""
from flask import Flask, jsonify, request
import pymysql
import os
import json
import time
from datetime import datetime

app = Flask(__name__)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': os.environ.get('DB_PASSWORD', 'WalletBackup2026!'),
    'database': 'wallet_backup',
    'charset': 'utf8mb4'
}

# PandaScore API配置
PANDASCORE_API_KEY = "your_pandascore_token_here"  # 从pandascoreapi.txt读取
PANDASCORE_BASE_URL = "https://api.pandascore.co"


def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)


@app.route('/api/points/balance', methods=['POST'])
def get_points_balance():
    """查询用户积分余额"""
    try:
        data = request.get_json(force=True)
        address = data.get('address')
        
        if not address:
            return jsonify({'success': False, 'message': '缺少address参数'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 查询积分余额
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


@app.route('/api/points/convert', methods=['POST'])
def convert_usdt_to_points():
    """USDT余额转换为积分 (1 USDT = 1 积分)"""
    try:
        data = request.get_json(force=True)
        address = data.get('address')
        usdt_amount = float(data.get('usdt_amount', 0))
        
        if not address or usdt_amount <= 0:
            return jsonify({'success': False, 'message': '参数错误'}), 400
        
        points_to_add = usdt_amount  # 1:1转换
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 检查用户是否存在
            cursor.execute('SELECT points FROM user_points WHERE address = %s', (address,))
            existing = cursor.fetchone()
            
            if existing:
                # 更新积分
                cursor.execute(
                    'UPDATE user_points SET points = points + %s, total_earned = total_earned + %s WHERE address = %s',
                    (points_to_add, points_to_add, address)
                )
                new_balance = existing[0] + points_to_add
            else:
                # 创建新用户
                cursor.execute(
                    'INSERT INTO user_points (address, points, total_earned) VALUES (%s, %s, %s)',
                    (address, points_to_add, points_to_add)
                )
                new_balance = points_to_add
            
            # 记录流水
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


@app.route('/api/bet/place', methods=['POST'])
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
            # 检查积分余额
            cursor.execute('SELECT points FROM user_points WHERE address = %s', (address,))
            user = cursor.fetchone()
            
            if not user or user['points'] < bet_amount:
                return jsonify({'success': False, 'message': '积分余额不足'}), 400
            
            # 扣除积分
            new_balance = user['points'] - bet_amount
            cursor.execute(
                'UPDATE user_points SET points = %s, total_spent = total_spent + %s WHERE address = %s',
                (new_balance, bet_amount, address)
            )
            
            # 创建竞猜记录
            potential_win = bet_amount * odds
            cursor.execute(
                'INSERT INTO betting_records (address, match_id, match_name, team_bet, bet_amount, odds, potential_win) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (address, match_id, match_name, team_bet, bet_amount, odds, potential_win)
            )
            bet_id = cursor.lastrowid
            
            # 记录流水
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


@app.route('/api/bet/history', methods=['POST'])
def get_bet_history():
    """查询用户竞猜历史"""
    try:
        data = request.get_json(force=True)
        address = data.get('address')
        
        if not address:
            return jsonify({'success': False, 'message': '缺少address参数'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute(
            'SELECT * FROM betting_records WHERE address = %s ORDER BY created_at DESC LIMIT 50',
            (address,)
        )
        records = cursor.fetchall()
        conn.close()
        
        # 转换Decimal为float
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


@app.route('/api/exchange/request', methods=['POST'])
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
            # 检查积分余额
            cursor.execute('SELECT points FROM user_points WHERE address = %s', (address,))
            user = cursor.fetchone()
            
            if not user or user['points'] < points_amount:
                return jsonify({'success': False, 'message': '积分余额不足'}), 400
            
            # 生成订单号
            order_no = f"EX{int(time.time())}{address[-6:]}"
            
            # 创建订单
            cursor.execute(
                'INSERT INTO exchange_orders (order_no, address, points_amount, usdt_amount, exchange_rate) VALUES (%s, %s, %s, %s, %s)',
                (order_no, address, points_amount, usdt_amount, exchange_rate)
            )
            order_id = cursor.lastrowid
            
            # 扣除积分
            new_balance = user['points'] - points_amount
            cursor.execute(
                'UPDATE user_points SET points = %s, total_spent = total_spent + %s WHERE address = %s',
                (new_balance, points_amount, address)
            )
            
            # 记录流水
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


@app.route('/api/exchange/history', methods=['POST'])
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
        
        # 转换Decimal为float
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
