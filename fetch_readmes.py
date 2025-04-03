import requests
import os
import base64

ORG_NAME = 'readme-hub-test'
OUTPUT_DIR = 'docs'

def fetch_readme(repo_name):
    url = f'https://api.github.com/repos/{ORG_NAME}/{repo_name}/readme'
    response = requests.get(url)
    if response.status_code == 200:
        readme_content = base64.b64decode(response.json()['content']).decode('utf-8')
        return readme_content
    return None

def save_readme(repo_name, content):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    file_path = os.path.join(OUTPUT_DIR, f'{repo_name}.md')
    with open(file_path, 'w') as file:
        file.write(content)

def main():
    url = f'https://api.github.com/orgs/{ORG_NAME}/repos'
    response = requests.get(url)
    repos = response.json()
    for repo in repos:
        repo_name = repo['name']
        readme_content = fetch_readme(repo_name)
        if readme_content:
            save_readme(repo_name, readme_content)

if __name__ == '__main__':
    main()
