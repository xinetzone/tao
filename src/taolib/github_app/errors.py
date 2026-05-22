class GitHubAppError(Exception):
    """Base error for the GitHub App integration."""


class GitHubAppConfigurationError(ValueError, GitHubAppError):
    """Raised when required GitHub App configuration is missing or invalid."""


class GitHubAppClientError(GitHubAppError):
    """Raised when the GitHub App client cannot obtain an installation token."""
