"""下载一些东西"""
from github import Github
from io import BytesIO


def get_github_content(user_name, repo_name, filename):
    """"""
    g = Github()
    user = g.get_user(user_name)
    repo = user.get_repo(repo_name)
    contents = repo.get_contents(filename)
    return contents.decoded_content.decode()


def iter_github_bytes(user_name, repo_name, root_dir):
    """"""
    g = Github()
    user = g.get_user(user_name)
    repo = user.get_repo(repo_name)
    contents = repo.get_contents(root_dir)
    for content in contents:
        yield BytesIO(content.decoded_content)
