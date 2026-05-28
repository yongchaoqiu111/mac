"""
GitHub图片密钥提取器 - 从公开图片文件名中提取密钥

原理：
1. 在GitHub创建公开仓库
2. 上传空图片，文件名为密钥（如：ClientWallet2026SecureKey32B!!!!.png）
3. 代码通过GitHub API读取文件名
4. 去掉扩展名得到真实密钥

优势：
- 密钥不存储在代码、环境变量、配置文件中
- GitHub公开仓库任何人都可访问，但没人知道文件名是密钥
- 可随时更换密钥（删除旧图片，上传新图片）
"""
import requests
import os


class GitHubImageKeyExtractor:
    """GitHub图片密钥提取器"""
    
    def __init__(self, repo_owner, repo_name, branch='main'):
        """
        初始化
        
        Args:
            repo_owner: GitHub用户名或组织名
            repo_name: 仓库名称
            branch: 分支名称
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.branch = branch
        self.api_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents'
    
    def extract_key_from_image(self, image_path, remove_extension=True):
        """
        从图片路径提取密钥
        
        Args:
            image_path: 图片在仓库中的路径（如：keys/client_key.png）
            remove_extension: 是否移除文件扩展名
            
        Returns:
            密钥字符串
        """
        if remove_extension:
            # 移除 .png/.svg/.jpg 等扩展名
            key = os.path.splitext(os.path.basename(image_path))[0]
        else:
            key = os.path.basename(image_path)
        
        return key
    
    def get_client_key(self):
        """获取客户端加密密钥"""
        try:
            # 方法1：直接指定文件名
            image_path = 'keys/client_encryption_key.png'
            return self.extract_key_from_image(image_path)
        
        except Exception as e:
            raise Exception(f"获取客户端密钥失败: {str(e)}")
    
    def get_server_key(self):
        """获取服务器加密密钥"""
        try:
            image_path = 'keys/server_encryption_key.png'
            return self.extract_key_from_image(image_path)
        
        except Exception as e:
            raise Exception(f"获取服务器密钥失败: {str(e)}")
    
    def list_all_keys(self):
        """
        列出仓库中所有图片文件名（用于调试）
        
        Returns:
            图片文件名列表
        """
        try:
            response = requests.get(
                f'{self.api_url}/keys',
                params={'ref': self.branch},
                timeout=10
            )
            
            if response.status_code != 200:
                raise Exception(f"GitHub API错误: {response.status_code}")
            
            files = response.json()
            image_files = []
            
            for file in files:
                if file['type'] == 'file' and file['name'].endswith(('.png', '.svg', '.jpg')):
                    key = self.extract_key_from_image(file['name'])
                    image_files.append({
                        'filename': file['name'],
                        'key': key,
                        'path': file['path']
                    })
            
            return image_files
        
        except Exception as e:
            raise Exception(f"列出密钥文件失败: {str(e)}")


def get_keys_from_github(repo_owner='your_username', repo_name='secret-keys'):
    """
    从GitHub获取加密密钥（便捷函数）
    
    Args:
        repo_owner: GitHub用户名
        repo_name: 仓库名称
        
    Returns:
        (client_key, server_key)
    """
    extractor = GitHubImageKeyExtractor(repo_owner, repo_name)
    
    client_key = extractor.get_client_key()
    server_key = extractor.get_server_key()
    
    return client_key, server_key


# ==================== 使用示例 ====================
if __name__ == '__main__':
    print("="*60)
    print(" GitHub图片密钥提取器测试")
    print("="*60)
    
    # 配置你的GitHub仓库
    REPO_OWNER = 'your_username'  # 改成你的GitHub用户名
    REPO_NAME = 'secret-keys'      # 改成你的仓库名
    
    print(f"\n仓库: https://github.com/{REPO_OWNER}/{REPO_NAME}")
    
    try:
        extractor = GitHubImageKeyExtractor(REPO_OWNER, REPO_NAME)
        
        # 列出所有密钥文件
        print("\n【列出所有密钥文件】")
        keys = extractor.list_all_keys()
        for key_info in keys:
            print(f"  文件: {key_info['filename']}")
            print(f"  密钥: {key_info['key'][:20]}...")
            print()
        
        # 获取具体密钥
        print("【获取客户端密钥】")
        client_key = extractor.get_client_key()
        print(f"  密钥: {client_key}")
        print(f"  长度: {len(client_key)} 字符")
        
        print("\n【获取服务器密钥】")
        server_key = extractor.get_server_key()
        print(f"  密钥: {server_key}")
        print(f"  长度: {len(server_key)} 字符")
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        print("\n使用前请：")
        print("1. 创建GitHub公开仓库")
        print("2. 上传空图片，文件名为密钥")
        print("   例如：ClientWallet2026SecureKey32B!!!!.png")
        print("3. 修改代码中的 REPO_OWNER 和 REPO_NAME")
