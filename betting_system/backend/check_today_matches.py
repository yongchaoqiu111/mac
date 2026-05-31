import sys
sys.path.insert(0, '/root/wallet/modules/betting_system')
from virtual_match_manager import VirtualMatchManager
from datetime import datetime, date

print("=== 检查比赛时间 ===\n")

manager = VirtualMatchManager()

# 1. 检查服务器时间
print(f"1. 服务器时间: {datetime.now()}")
print(f"2. 今天日期: {date.today()}\n")

# 2. 查询今日比赛
manager.cursor.execute('''
    SELECT id, game, match_time, status, winner
    FROM virtual_matches
    WHERE DATE(match_time) = %s
    ORDER BY match_time
    LIMIT 10
''', (date.today(),))

matches = manager.cursor.fetchall()

print(f"3. 今日比赛数量: {len(matches)}")
print("\n前10场比赛:")
for m in matches:
    print(f"  ID:{m['id']} | {m['game']} | {m['match_time']} | {m['status']} | winner:{m['winner']}")

# 3. 检查是否有今天的比赛
if len(matches) == 0:
    print("\n⚠️ 今日没有比赛！需要重新生成")
else:
    print(f"\n✅ 今日有 {len(matches)} 场比赛")

manager.close()
