import pymysql
from datetime import datetime, timedelta

conn = pymysql.connect(
    host='47.83.0.101',
    user='root',
    password='WalletBackup2026!',
    database='wallet_backup'
)
cursor = conn.cursor()

now = datetime.now()
two_minutes_later = now + timedelta(minutes=2)

print(f"当前时间: {now}")
print(f"2分钟后: {two_minutes_later}")
print(f"\n应该转为live的比赛（match_time <= {two_minutes_later}）:")

cursor.execute('''
    SELECT id, game, match_time, status FROM virtual_matches 
    WHERE status = 'pending' AND match_time <= %s AND DATE(match_time) = CURDATE()
    ORDER BY match_time
''', (two_minutes_later,))

matches = cursor.fetchall()
print(f"找到 {len(matches)} 场比赛")

for m in matches:
    print(f"  {m[0]}: {m[1]} - {m[2]} ({m[3]})")

if len(matches) > 0:
    print(f"\n执行更新...")
    cursor.execute('''
        UPDATE virtual_matches 
        SET status = 'live'
        WHERE status = 'pending' AND match_time <= %s AND DATE(match_time) = CURDATE()
    ''', (two_minutes_later,))
    
    conn.commit()
    print(f"已更新 {cursor.rowcount} 场比赛为live状态")
    
    # 再次查询验证
    cursor.execute('''
        SELECT status, COUNT(*) FROM virtual_matches 
        WHERE DATE(match_time) = CURDATE() GROUP BY status
    ''')
    print(f"\n各状态统计:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

conn.close()
