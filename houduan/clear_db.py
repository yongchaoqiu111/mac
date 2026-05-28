import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'wallet_backup',
    'charset': 'utf8mb4'
}

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()
cursor.execute("DELETE FROM wallet_backups")
conn.commit()
print(f"已删除 {cursor.rowcount} 条记录")
cursor.close()
conn.close()
