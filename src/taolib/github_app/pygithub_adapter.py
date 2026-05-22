from github import Auth, Github

from taolib.github_app.config import GitHubAppSettings
from taolib.github_app.models import InstallationTokenRequest
from taolib.github_app.token_manager import GitHubInstallationTokenManager


class PyGithubInstallationClientFactory:
    def __init__(
        self,
        settings: GitHubAppSettings,
        manager: GitHubInstallationTokenManager,
    ) -> None:
        self.settings = settings
        self.manager = manager

    async def create(self, request: InstallationTokenRequest) -> Github:
        result = await self.manager.get_token(request)
        auth = Auth.Token(result.token)
        return Github(auth=auth, base_url=self.settings.api_url)


async def build_pygithub_client(
    settings: GitHubAppSettings,
    manager: GitHubInstallationTokenManager,
    request: InstallationTokenRequest,
) -> Github:
    factory = PyGithubInstallationClientFactory(settings=settings, manager=manager)
    return await factory.create(request)
