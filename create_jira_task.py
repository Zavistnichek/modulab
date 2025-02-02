from jira import JIRA
import os
import re
import sys
import logging
import subprocess


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_jira_task():
    jira_server = os.environ.get("JIRA_SERVER")
    jira_email = os.environ.get("JIRA_EMAIL")
    jira_api_token = os.environ.get("JIRA_API_TOKEN")

    if not jira_server or not jira_email or not jira_api_token:
        logger.error(
            "Missing Jira credentials (JIRA_SERVER, JIRA_EMAIL, JIRA_API_TOKEN)"
        )
        sys.exit(1)

    try:
        jira = JIRA(server=jira_server, basic_auth=(jira_email, jira_api_token))
        commit_message = get_commit_message()
        issue_key = extract_jira_issue_key(commit_message)

        if issue_key:
            logger.info(f"Jira issue key found: {issue_key}")
        else:
            logger.warning("No Jira issue key found in commit message")

        issue = jira.create_issue(
            project="DPJ",
            summary=f"New commit: {commit_message}",
            description=f"Commit message: {commit_message}",
            issuetype={"name": "Task"},
        )

        logger.info(f"Successfully created Jira task: {issue.key}")
        return issue.key
    except Exception as e:
        logger.error(f"Error creating Jira task: {e}")
        sys.exit(1)


def get_commit_message():
    """Функция для получения сообщения последнего коммита"""
    try:
        commit_message = subprocess.check_output(
            ["git", "log", "-1", "--pretty=%B"], text=True
        ).strip()
        return commit_message
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting commit message: {e}")
        sys.exit(1)


def extract_jira_issue_key(commit_message):
    """Функция для извлечения ключа задачи из сообщения коммита."""
    match = re.search(r"\b[A-Z]{2,}-\d+\b", commit_message)
    if match:
        return match.group(0)
    return None


if __name__ == "__main__":
    create_jira_task()
