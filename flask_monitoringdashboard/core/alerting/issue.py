import requests

from flask_monitoringdashboard.core.alerting.alert_content import AlertContent

GITHUB_CHAR_LIMIT = 60000


def get_issue_endpoint_url(repo_owner: str, repo_name: str):
    return f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"


def make_issue_post_request(github_token: str, repo_owner: str, repo_name: str, data):
    url = get_issue_endpoint_url(repo_owner, repo_name)
    headers = _post_headers(github_token)

    return requests.post(url, headers=headers, json=data, timeout=10)


def create_issue(
        github_token: str,
        repo_owner: str,
        repo_name: str,
        alert_content: AlertContent):
    is_user_captured_label = "user-captured" if alert_content.is_user_captured else "uncaught"
    data = {
        "title": alert_content.title,
        "body": alert_content.create_body_markdown(GITHUB_CHAR_LIMIT),
        "labels": ["automated-issue", "exception", is_user_captured_label]
    }

    try:
        resp = make_issue_post_request(github_token, repo_owner, repo_name, data)
        resp.raise_for_status()
    except Exception as e:
        print("Error creating GitHub issue alert:", e)


def _post_headers(github_token: str):
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    return headers
