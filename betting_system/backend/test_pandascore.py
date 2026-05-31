import requests
import json

# PandaScore API配置
API_KEY = "7SU7xFYhMi2z3Otlw89M1x53Ln4b10qWBiZQmY6bz86QgQ7Gf0Q"  # 替换为真实的API Key
BASE_URL = "https://api.pandascore.co"

def test_pandascore_matches():
    """测试获取赛事数据"""
    print("=" * 60)
    print("测试PandaScore赛事数据")
    print("=" * 60)
    
    # 测试不同的游戏类型
    games = ['lol', 'dota2', 'csgo']
    
    for game in games:
        print(f"\n 测试游戏: {game.upper()}")
        print("-" * 60)
        
        try:
            url = f"{BASE_URL}/matches/upcoming"
            headers = {'Authorization': f'Bearer {API_KEY}'}
            params = {
                'filter[videogame]': game,
                'page': 1,
                'per_page': 20
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                matches = response.json()
                print(f"✅ 成功获取 {len(matches)} 场赛事")
                
                # 显示前3场赛事信息
                if len(matches) > 0:
                    print(f"\n📋 前3场赛事示例:")
                    for i, match in enumerate(matches[:3], 1):
                        teams = match.get('opponents', [])
                        team_names = []
                        for team in teams:
                            opponent = team.get('opponent', {})
                            if opponent:
                                team_names.append(opponent.get('name', '未知'))
                        
                        begin_at = match.get('begin_at', 'N/A')
                        league = match.get('league', {})
                        league_name = league.get('name', 'N/A') if league else 'N/A'
                        
                        print(f"  {i}. {team_names[0] if len(team_names) > 0 else '未知'} vs {team_names[1] if len(team_names) > 1 else '未知'}")
                        print(f"     联赛: {league_name}")
                        print(f"     时间: {begin_at}")
                        print()
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == '__main__':
    test_pandascore_matches()
