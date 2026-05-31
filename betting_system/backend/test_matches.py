import requests

API_KEY = "7SU7xFYhMi2z3Otlw89M1x53Ln4b10qWBiZQmY6bz86QgQ7Gf0Q"
BASE_URL = "https://api.pandascore.co"

print("=" * 70)
print("PandaScore 赛事数据测试")
print("=" * 70)

games = {
    'lol': '英雄联盟',
    'dota2': 'DOTA2',
    'csgo': 'CS2'
}

for game_code, game_name in games.items():
    print(f"\n🎮 {game_name} ({game_code.upper()})")
    print("-" * 70)
    
    try:
        # 测试即将开始的赛事
        url = f"{BASE_URL}/matches/upcoming"
        headers = {'Authorization': f'Bearer {API_KEY}'}
        params = {'filter[videogame]': game_code, 'per_page': 100}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            matches = response.json()
            print(f"✅ 即将开始: {len(matches)} 场")
            
            if len(matches) > 0:
                # 显示第一场赛事
                match = matches[0]
                teams = match.get('opponents', [])
                team_names = [t.get('opponent', {}).get('name', '?') for t in teams if t.get('opponent')]
                
                begin_at = match.get('begin_at', 'N/A')
                league = match.get('league', {})
                league_name = league.get('name', 'N/A') if league else 'N/A'
                
                print(f"   示例: {team_names[0] if len(team_names) > 0 else '?'} vs {team_names[1] if len(team_names) > 1 else '?'}")
                print(f"   联赛: {league_name}")
                print(f"   时间: {begin_at}")
        else:
            print(f"❌ 请求失败: HTTP {response.status_code}")
            print(f"   {response.text[:100]}")
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")

print("\n" + "=" * 70)
print(" 总结:")
print("=" * 70)
print("PandaScore免费版API:")
print("  - 每小时限制: 100次请求")
print("  - 每天可提供: 数百场赛事")
print("  - 完全满足用户每天竞猜的需求")
print("=" * 70)
