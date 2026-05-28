# MySQL数据库安装指南

## 推荐版本
- **MySQL 8.0** (最新稳定版)
- 下载地址: https://dev.mysql.com/downloads/mysql/

## Windows安装步骤

### 1. 下载MySQL Installer
1. 访问: https://dev.mysql.com/downloads/installer/
2. 选择 **mysql-installer-community-8.0.xx.msi**
3. 推荐下载完整安装包 (~500MB)

### 2. 安装配置
运行安装程序，选择以下选项：

```
安装类型: Server only (仅服务器)
配置类型: Development Computer (开发计算机)
端口: 3306 (默认)
root密码: your_password (记住这个密码！)
```

### 3. 安装完成验证

打开PowerShell，运行：
```powershell
mysql -u root -p
```
输入刚才设置的密码，如果能进入MySQL命令行，说明安装成功。

## 配置数据库

安装成功后，MySQL会自动创建数据库。代码中已配置自动创建 `wallet_backup` 数据库。

## 修改服务器配置

编辑 `f:\qianbao\houduan\server.py`，修改数据库密码：

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '你设置的MySQL密码',  # 改成你的密码
    'database': 'wallet_backup',
    'charset': 'utf8mb4'
}
```

## 启动服务器

```powershell
C:\Users\Administrator\AppData\Local\Programs\Python\Python313\python.exe f:\qianbao\houduan\server.py
```

看到 "✅ 数据库初始化完成" 即表示成功！

## 注意事项
- 确保MySQL服务正在运行 (Windows服务: MySQL80)
- 防火墙放行3306端口
- 记住root密码，后续配置需要
