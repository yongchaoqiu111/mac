import os
import requests


GITHUB_REPO_OWNER = 'yongchaoqiu111'
GITHUB_REPO_NAME = 'plaint'
GITHUB_BRANCH = 'main'


def get_key_from_github(extension='.ico'):
    url = f'https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/contents/'
    response = requests.get(url)
    response.raise_for_status()
    
    files = response.json()
    for file in files:
        if file['name'].endswith(extension):
            filename = file['name']
            key = os.path.splitext(filename)[0]
            return key
    
    raise FileNotFoundError(f"No {extension} file found in GitHub repo")


def get_encryption_keys():
    client_key_str = get_key_from_github('.ico')
    server_key_str = get_key_from_github('.png')
    
    client_key = client_key_str.encode('utf-8')
    server_key = server_key_str.encode('utf-8')
    
    if len(client_key) != 32 or len(server_key) != 32:
        raise ValueError(f"Key length error: requires 32 bytes")
    
    return client_key, server_key


if __name__ == '__main__':
    client_key, server_key = get_encryption_keys()
    print(f"Client Key: {client_key}")
    print(f"Server Key: {server_key}")
