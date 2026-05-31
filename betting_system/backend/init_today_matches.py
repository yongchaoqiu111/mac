import sys
sys.path.insert(0, '/root/wallet/modules/betting_system')
from virtual_match_manager import VirtualMatchManager

m = VirtualMatchManager()
m.generate_daily_matches()
m.close()
