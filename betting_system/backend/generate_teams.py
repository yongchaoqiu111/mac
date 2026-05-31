"""生成虚拟队伍数据 - 每个游戏72支队伍"""
import pymysql
import os

# 数据库配置
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'WalletBackup2026!'),
    'database': os.environ.get('DB_NAME', 'wallet_backup'),
    'charset': 'utf8mb4'
}

# 队伍名称池
TEAM_NAMES = {
    'lol': [
        'Dragon Warriors', 'Phoenix Rising', 'Shadow Knights', 'Thunder Strike',
        'Frost Guardians', 'Blaze Runners', 'Storm Eagles', 'Night Hunters',
        'Crystal Mages', 'Iron Wolves', 'Fire Dragons', 'Lightning Titans',
        'Dark Assassins', 'Holy Paladins', 'Venom Snakes', 'Golden Lions',
        'Silver Foxes', 'Crimson Blades', 'Azure Hawks', 'Emerald Panthers',
        'Ruby Tigers', 'Diamond Bears', 'Platinum Rhinos', 'Obsidian Dragons',
        'Jade serpents', 'Sapphire Eagles', 'Topaz Falcons', 'Opal Wolves',
        'Amber Bears', 'Pearl Panthers', 'Coral Tigers', 'Onyx Lions',
        'Ivory Knights', 'Ebony Warriors', 'Scarlet Phoenixes', 'Violet Shadows',
        'Indigo Storms', 'White Knights', 'Black Demons', 'Red Dragons',
        'Blue Titans', 'Green Guardians', 'Yellow Lightning', 'Purple Mages',
        'Orange Flames', 'Cyan Frost', 'Magenta Blades', 'Teal Hunters',
        'Maroon Wolves', 'Navy Eagles', 'Olive Panthers', 'Khaki Tigers',
        'Beige Lions', 'Gray Knights', 'Brown Warriors', 'Tan Phoenixes',
        'Cream Shadows', 'Pink Storms', 'Rose Knights', 'Lilac Demons',
        'Lavender Dragons', 'Mint Titans', 'Sky Guardians', 'Steel Lightning',
        'Iron Mages', 'Copper Blades', 'Bronze Hunters', 'Gold Wolves',
        'Silver Eagles', 'Platinum Panthers', 'Titanium Tigers', 'Chromium Lions',
        'Cobalt Knights', 'Nickel Warriors', 'Zinc Phoenixes', 'Lead Shadows',
        'Tin Storms', 'Brass Knights', 'Chrome Demons', 'Aluminum Dragons'
    ],
    'dota2': [
        'Ancient Guardians', 'Roshan Slayers', 'Aegis Holders', 'Divine Rapier',
        'Black King Bar', 'Heart of Tarrasque', 'Butterfly Wings', 'Daedalus Strike',
        'Monkey King Bar', 'Battle Fury', 'Radiance Burn', 'Desolator Touch',
        'Shadow Blade', 'Force Staff', 'Blink Dagger', 'Aghanim Scepter',
        'Refresher Orb', 'Scythe of Vyse', 'Eye of Skadi', 'Satanic Power',
        'Mjollnir Storm', 'Assault Cuirass', 'Shivas Guard', 'Vladmir Offering',
        'Pipe of Insight', 'Crimson Guard', 'Lotus Orb', 'Solar Crest',
        'Glimmer Cape', 'Aether Lens', 'Octarine Core', 'Bloodthorn Thorn',
        'Ethereal Blade', 'Diffusal Blade', 'Manta Style', 'Yasha Swift',
        'Sange and Yasha', 'Kaya and Sange', 'Kaya and Yasha', 'Hurricane Pike',
        'Eul Scepter', 'Rod of Atos', 'Vanguard Shield', 'Blade Mail',
        'Drum of Endurance', 'Mekansm Heal', 'Buckler Shield', 'Ring of Basilius',
        'Headdress Restore', 'Medallion Courage', 'Solar Crest Light', 'Veil Discord',
        'Necronomicon Army', 'Urns of Shadows', 'Spirit Vessel', 'Echo Sabre',
        'Silver Edge', 'Nullifier', 'Abyssal Blade', 'Bloodstone Sanguine',
        'Guardian Greaves', 'Arcane Boots', 'Phase Boots', 'Power Treads',
        'Tranquil Boots', 'Boots of Travel', 'Hand of Midas', 'Orchid Malevolence'
    ],
    'csgo': [
        'AK Masters', 'AWP Legends', 'Deagle Kings', 'Glock Warriors',
        'USP Assassins', 'M4A4 Elite', 'M4A1S Shadows', 'P90 Rush',
        'MP7 Storm', 'FAMAS Force', 'Galil AR Fire', 'SG 553 Strike',
        'AUG Aim', 'SSG 08 Snipers', 'SCAR-20 Scope', 'G3SG1 Guns',
        'Nova Blast', 'XM1014 Shot', 'MAG-7 Fury', 'Sawed-Off Skull',
        'M249 Heavy', 'Negev Nemesis', 'Dual Berettas', 'Five-SeveN',
        'Tec-9 Terror', 'CZ75-Auto', 'P2000 Pistol', 'P250 Power',
        'R8 Revolver', 'MAC-10 Machine', 'UMP-45 Urban', 'PP-Bizon',
        'Helical Helix', 'MP5-SD Silent', 'Zeus x27 Thunder', 'Knife Masters',
        'Bomb Defusers', 'Hostage Rescuers', 'Clutch Kings', 'Ace Hunters',
        'Flawless Victory', 'Headshot Heroes', 'Spray Control', 'Crosshair Pro',
        'Smoke Strategy', 'Flash Bang', 'Molotov Masters', 'HE Grenade',
        'Decoy Experts', 'Tactical Team', 'Eco Round', 'Force Buy',
        'Full Buy Squad', 'Pistol Round', 'Anti-Eco', 'Meta Masters',
        'Frag Leaders', 'Entry Fraggers', 'Support Stars', 'IGL Legends',
        'AWPer Elite', 'Rifler Pro', 'Lurker Shadow', 'Anchor Defender'
    ]
}

def generate_teams():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    for game, teams in TEAM_NAMES.items():
        for team_name in teams:
            try:
                cursor.execute(
                    'INSERT IGNORE INTO virtual_teams (game, team_name) VALUES (%s, %s)',
                    (game, team_name)
                )
            except Exception as e:
                print(f"插入失败 {team_name}: {e}")
    
    conn.commit()
    cursor.execute('SELECT COUNT(*) FROM virtual_teams')
    total = cursor.fetchone()[0]
    print(f"成功生成 {total} 支队伍！")
    
    conn.close()

if __name__ == '__main__':
    generate_teams()
