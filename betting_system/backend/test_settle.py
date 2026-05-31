import sys
sys.path.insert(0, '/root/wallet/modules/betting_system')
from virtual_match_manager import VirtualMatchManager

print("=== 测试自动结算功能 ===\n")

manager = VirtualMatchManager()

# 1. 先查看有哪些live状态的比赛
print("1. 查询live状态的比赛:")
manager.cursor.execute('''
    SELECT id, game, match_time, status FROM virtual_matches 
    WHERE status = 'live' LIMIT 5
''')
live_matches = manager.cursor.fetchall()
if live_matches:
    for m in live_matches:
        print(f"   比赛ID: {m['id']}, 游戏: {m['game']}, 时间: {m['match_time']}")
else:
    print("   没有live状态的比赛")

# 2. 将所有pending比赛改为live（模拟赛前2分钟）
print("\n2. 将所有pending比赛转为live状态...")
manager.cursor.execute('''
    UPDATE virtual_matches SET status = 'live' WHERE status = 'pending'
''')
affected = manager.cursor.rowcount
manager.conn.commit()
print(f"   转换了 {affected} 场比赛为live状态")

# 3. 执行结算（需要比赛时间超过1小时）
print("\n3. 执行自动结算...")
manager.settle_matches()

# 4. 查看结算结果
print("\n4. 查询finished状态的比赛:")
manager.cursor.execute('''
    SELECT id, game, winner, status FROM virtual_matches 
    WHERE status = 'finished' LIMIT 5
''')
finished_matches = manager.cursor.fetchall()
if finished_matches:
    for m in finished_matches:
        print(f"   比赛ID: {m['id']}, 获胜方: {m['winner']}")
else:
    print("   没有已结算的比赛")

manager.close()
print("\n=== 测试完成 ===")
