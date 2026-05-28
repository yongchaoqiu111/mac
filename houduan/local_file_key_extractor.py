"""
本地文件密钥提取器 - 从ICO/PNG文件名中提取密钥

原理：
1. 将密钥作为文件名（文件名就是密钥本身）
2. 代码读取文件名，去掉扩展名得到密钥
3. 文件可以放在任何位置（本地/网络/GitHub）

优势：
- 极简实现，无需API调用
- 文件可以放在任何可访问的位置
- 更换密钥只需重命名文件
- 代码中没有任何密钥信息
"""
import os


def extract_key_from_filename(file_path):
    """
    从文件路径提取密钥（去掉扩展名）
    
    Args:
        file_path: 文件完整路径
        
    Returns:
        密钥字符串
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"密钥文件不存在: {file_path}")
    
    # 获取文件名（不含路径和扩展名）
    filename = os.path.basename(file_path)
    key = os.path.splitext(filename)[0]
    
    return key


def get_client_key():
    """获取客户端加密密钥"""
    # 硬编码文件路径 - 改成你的实际文件位置
    KEY_FILE_PATH = r'你的客户端密钥文件路径.ico'
    
    return extract_key_from_filename(KEY_FILE_PATH)


def get_server_key():
    """获取服务器加密密钥"""
    # 硬编码文件路径 - 改成你的实际文件位置
    KEY_FILE_PATH = r'你的服务器密钥文件路径.png'
    
    return extract_key_from_filename(KEY_FILE_PATH)


def get_keys():
    """
    获取双重加密密钥
    
    Returns:
        (client_key, server_key)
    """
    client_key = get_client_key()
    server_key = get_server_key()
    
    return client_key, server_key


# ==================== 使用示例 ====================
if __name__ == '__main__':
    print("="*60)
    print(" 本地文件密钥提取器")
    print("="*60)
    
    try:
        # 获取密钥
        client_key, server_key = get_keys()
        
        print(f"\n✅ 客户端密钥: {client_key}")
        print(f"   长度: {len(client_key)} 字符")
        
        print(f"\n✅ 服务器密钥: {server_key}")
        print(f"   长度: {len(server_key)} 字符")
        
        print("\n📝 使用说明:")
        print("  1. 重命名文件，将密钥作为文件名")
        print("     例如：your_actual_key_here.ico")
        print("  2. 修改代码中的 KEY_FILE_PATH 指向你的文件")
        print("  3. 运行程序自动提取密钥")
        print("\n⚠️  注意：代码中不包含任何密钥信息，密钥仅在文件名中")
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        print("\n请确保:")
        print("  1. 文件存在且路径正确")
        print("  2. 文件名就是密钥（不含扩展名）")
