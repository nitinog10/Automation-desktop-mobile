"""
github_bot.py – GitHub API Automation
========================================
Uses the GitHub REST API to create repositories, push READMEs,
and manage files. Requires a GitHub Personal Access Token.

Usage:
    from automation.github_bot import create_repo, add_file
    create_repo("my-awesome-project")
    add_file("my-awesome-project", "hello.txt", "Hello World!")
"""

import logging
import requests

logger = logging.getLogger(__name__)

_API_BASE = "https://api.github.com"


def _get_headers() -> dict:
    """Build GitHub API auth headers."""
    from config import GITHUB_TOKEN

    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN not set in .env")

    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }


def create_repo(
    repo_name: str,
    description: str = "Created by GitWake Assistant 🚀",
    private: bool = False,
    auto_init: bool = True,
) -> str:
    """
    Create a new GitHub repository.

    Args:
        repo_name: Name of the repository.
        description: Repo description.
        private: Whether the repo is private.
        auto_init: Whether to initialize with a README.

    Returns:
        Result message with repo URL.
    """
    if not repo_name:
        return "⚠️ Repository name is required."

    try:
        headers = _get_headers()
    except ValueError as e:
        return f"❌ {e}"

    payload = {
        "name": repo_name,
        "description": description,
        "private": private,
        "auto_init": auto_init,
    }

    try:
        resp = requests.post(f"{_API_BASE}/user/repos", json=payload, headers=headers)

        if resp.status_code == 201:
            url = resp.json().get("html_url", "")
            logger.info(f"Created GitHub repo: {url}")
            return f"✅ GitHub repo created: {url}"
        elif resp.status_code == 422:
            return f"⚠️ Repo '{repo_name}' already exists."
        else:
            error = resp.json().get("message", resp.text)
            return f"❌ GitHub error ({resp.status_code}): {error}"

    except requests.RequestException as e:
        logger.error(f"GitHub API error: {e}")
        return f"❌ GitHub API error: {e}"


def add_file(
    repo_name: str,
    file_path: str,
    content: str,
    message: str = "Add file via GitWake Assistant",
) -> str:
    """
    Add or update a file in a GitHub repository.

    Args:
        repo_name: Name of the repository.
        file_path: Path within the repo (e.g., "docs/notes.md").
        content: File content (text).
        message: Commit message.

    Returns:
        Result message.
    """
    import base64

    try:
        headers = _get_headers()
        from config import GITHUB_USERNAME
    except ValueError as e:
        return f"❌ {e}"

    encoded = base64.b64encode(content.encode()).decode()
    payload = {
        "message": message,
        "content": encoded,
    }

    try:
        url = f"{_API_BASE}/repos/{GITHUB_USERNAME}/{repo_name}/contents/{file_path}"

        # Check if file already exists (need sha for update)
        existing = requests.get(url, headers=headers)
        if existing.status_code == 200:
            payload["sha"] = existing.json().get("sha", "")

        resp = requests.put(url, json=payload, headers=headers)

        if resp.status_code in (200, 201):
            logger.info(f"Added {file_path} to {repo_name}")
            return f"✅ File '{file_path}' added to {repo_name}"
        else:
            error = resp.json().get("message", resp.text)
            return f"❌ GitHub error: {error}"

    except requests.RequestException as e:
        logger.error(f"GitHub add_file error: {e}")
        return f"❌ GitHub API error: {e}"


def list_repos(limit: int = 10) -> str:
    """List the user's most recent repositories."""
    try:
        headers = _get_headers()
    except ValueError as e:
        return f"❌ {e}"

    try:
        resp = requests.get(
            f"{_API_BASE}/user/repos",
            headers=headers,
            params={"sort": "updated", "per_page": limit},
        )

        if resp.status_code == 200:
            repos = resp.json()
            if not repos:
                return "📂 No repositories found."

            lines = ["📂 Your repos:"]
            for r in repos:
                visibility = "🔒" if r.get("private") else "🌐"
                lines.append(f"  {visibility} {r['name']} – {r.get('description', '')}")
            return "\n".join(lines)
        else:
            return f"❌ GitHub error: {resp.text}"

    except requests.RequestException as e:
        return f"❌ GitHub API error: {e}"


def delete_repo(repo_name: str) -> str:
    """
    Delete a GitHub repository.

    Args:
        repo_name: Name of the repository to delete.

    Returns:
        Result message.
    """
    if not repo_name:
        return "⚠️ Repository name is required."

    try:
        headers = _get_headers()
        from config import GITHUB_USERNAME
    except ValueError as e:
        return f"❌ {e}"

    try:
        resp = requests.delete(
            f"{_API_BASE}/repos/{GITHUB_USERNAME}/{repo_name}",
            headers=headers,
        )

        if resp.status_code == 204:
            logger.info(f"Deleted GitHub repo: {repo_name}")
            return f"✅ GitHub repo '{repo_name}' deleted successfully."
        elif resp.status_code == 404:
            return f"⚠️ Repo '{repo_name}' not found."
        elif resp.status_code == 403:
            return f"❌ Permission denied. Your token needs 'delete_repo' scope."
        else:
            error = resp.json().get("message", resp.text)
            return f"❌ GitHub error ({resp.status_code}): {error}"

    except requests.RequestException as e:
        logger.error(f"GitHub delete_repo error: {e}")
        return f"❌ GitHub API error: {e}"
