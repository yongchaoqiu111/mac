# 电竞竞猜系统

## 模块说明
完全独立的竞猜系统模块，可自由组合到任何项目中。

## 目录结构
```
betting_system/
── frontend/          # Flutter前端模块
│   ├── betting_api_service.dart    # API服务
│   ├── points_page.dart           # 积分页面
│   ├── betting_page.dart          # 竞猜页面
│   ├── exchange_page.dart         # 兑换页面
│   └── transactions_page.dart     # 账单页面（积分流水）
├── backend/           # Python后端模块
│   ├── routes.py                  # API路由
│   ├── database.py                # 数据库配置
│   └── pandascore.py              # PandaScore对接
└── BETTING_API_DOC.md            # 对接文档
```

## 快速集成

### 1. 后端部署
```bash
# 复制backend文件夹到服务器
scp -r backend/* root@服务器IP:/root/wallet/modules/betting_system/

# 安装依赖
pip install flask pymysql requests

# 运行服务
python routes.py
```

### 2. 前端集成
```dart
// 在pubspec.yaml添加依赖
dependencies:
  betting_system:
    path: ../betting_system/frontend

// 在main.dart导入
import 'package:betting_system/betting_page.dart';
```

### 3. Nginx配置
```nginx
location /api/matches/ {
    proxy_pass http://127.0.0.1:5004;
}

location /api/bet/ {
    proxy_pass http://127.0.0.1:5004;
}

location /api/points/ {
    proxy_pass http://127.0.0.1:5004;
}

location /api/exchange/ {
    proxy_pass http://127.0.0.1:5004;
}
```

## 核心功能

### 赛事数据板块
- 赛事列表查询（支持游戏类型筛选：LOL、DOTA2、CSGO）
- 赛事状态筛选：即将开始、进行中、已结束
- 赛事详情和赔率查询
- 从PandaScore自动同步赛事数据
- 分页支持

**赛事数据量（PandaScore免费版）：**
- 🎮 英雄联盟 (LOL): ~85场/天
-  DOTA2: ~43场/天
-  CS2 (CSGO): ~100场/天
- **总计: ~228场/天** ✅ 完全满足每天竞猜需求

### 参与竞猜板块
- 下注竞猜（选择赛事、队伍、下注积分）
- 查询我的竞猜记录（支持状态筛）
- 竞猜结算（赢奖发放、输奖记录）
- 竞猜账单自动记录到积分流水

### 积分系统
- USDT余额 → 等额积分（1:1）
- 积分流水记录（账单页面）
- 积分余额查询
- 流水类型：转换、下注、赢奖、输奖、兑换

### 兑换系统
- 积分兑换USDT申请
- 后台审核兑换订单
- 兑换历史记录

### 竞猜系统
- 获取PandaScore比赛数据
- 用户下注
- 自动结算
- 竞猜历史

### 兑换系统
- 积分兑换USDT
- 订单管理
- 后台审核

## API接口

### 赛事数据板块

#### 1. 获取赛事列表
```http
POST /api/matches/list
Content-Type: application/json

{
  "game": "lol",        // 游戏类型：all, lol, dota2, csgo
  "status": "upcoming",  // 状态：upcoming, live, finished
  "page": 1              // 页码
}
```

#### 2. 获取赛事详情
```http
POST /api/matches/detail
Content-Type: application/json

{
  "match_id": 1
}
```

#### 3. 同步赛事数据（管理员）
```http
POST /api/matches/sync
Content-Type: application/json

{
  "game": "lol"  // 要同步的游戏类型
}
```

### 参与竞猜板块

#### 4. 下注竞猜
```http
POST /api/bet/place
Content-Type: application/json

{
  "address": "Txxxxxxxxx",
  "match_id": 1,
  "match_name": "T1 vs Gen.G",
  "team_bet": "T1",
  "bet_amount": 100,
  "odds": 1.85
}
```

#### 5. 查询我的竞猜记录
```http
POST /api/bet/my-bets
Content-Type: application/json

{
  "address": "Txxxxxxxxx",
  "status": "all"  // 状态：all, pending, won, lost
}
```

#### 6. 竞猜结算（管理员）
```http
POST /api/bet/settle
Content-Type: application/json

{
  "bet_id": 123,
  "is_win": true,
  "actual_win": 185
}
```

### 积分管理

#### 7. 查询积分余额
```http
POST /api/points/balance
Content-Type: application/json

{
  "address": "Txxxxxxxxx"
}
```

#### 8. USDT转换积分
```http
POST /api/points/convert
Content-Type: application/json

{
  "address": "Txxxxxxxxx",
  "usdt_amount": 100
}
```

#### 9. 查询积分流水（账单）
```http
POST /api/points/transactions
Content-Type: application/json

{
  "address": "Txxxxxxxxx"
}
```

### 兑换系统

#### 10. 申请积分兑换USDT
```http
POST /api/exchange/request
Content-Type: application/json

{
  "address": "Txxxxxxxxx",
  "points_amount": 500,
  "usdt_amount": 500,
  "exchange_rate": 1.0
}
```

#### 11. 查询兑换历史
```http
POST /api/exchange/history
Content-Type: application/json

{
  "address": "Txxxxxxxxx"
}
```

## 联系方式
- 开发者: Chase Qiu
- 邮箱: qiuyongchao@ai656.top
