from jira import JIRA
import os
import re
import sys


def create_jira_task():
    jira_server = os.environ["JIRA_SERVER"]
    jira_email = os.environ["JIRA_EMAIL"]
    jira_api_token = os.environ["JIRA_API_TOKEN"]

    try:
        jira = JIRA(server=jira_server, basic_auth=(jira_email, jira_api_token))
        commit_message = os.popen("git log -1 --pretty=%B").read().strip()
        issue_key = extract_jira_issue_key(commit_message)

        if issue_key is None:
            raise ValueError("Jira issue key not found in commit message")

        issue = jira.create_issue(
            project="PROJECT_KEY",  # Замените на ваш ключ проекта
            summary=f"New commit: {commit_message}",
            description=f"Commit message: {commit_message}",
            issuetype={"name": "Task"},
        )

        print(f"Successfully created Jira task: {issue.key}")
        return issue.key
    except Exception as e:
        print(f"Error creating Jira task: {e}")
        sys.exit(1)


def extract_jira_issue_key(commit_message):
    """Function to extract the issue key from the commit message."""
    match = re.search(r"\b[A-Z]{2,}-\d+\b", commit_message)
    if match:
        return match.group(0)
    return None


if __name__ == "__main__":
    create_jira_task()
