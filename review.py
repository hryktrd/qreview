"""QReview – GitHub PR auto-reviewer powered by Qwen3-Coder via ollama-control-plane."""
import logging
import os
import sys

from github import Github
from ollama import Client

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

MAX_DIFF_CHARS = 12_000

SYSTEM_PROMPT = """\
You are an expert code reviewer. Review the provided git diff and give feedback on:
1. Bugs and logic errors
2. Security issues (injection, secret exposure, broken auth, etc.)
3. Code quality and readability
4. Performance concerns
5. Missing error handling or edge cases
6. Test coverage gaps

Be concise and actionable. Format your response in Markdown.
Respond in the same language as the PR title/description when detectable; otherwise use English.\
"""


def get_pr_diff(repo, pr_number: int) -> str:
    pr = repo.get_pull(pr_number)
    parts: list[str] = []
    total = 0
    for f in pr.get_files():
        patch = f.patch or ""
        header = f"--- a/{f.filename}\n+++ b/{f.filename}\n"
        chunk = header + patch
        if total + len(chunk) > MAX_DIFF_CHARS:
            remaining = MAX_DIFF_CHARS - total
            if remaining > len(header):
                parts.append(header + patch[: remaining - len(header)])
            break
        parts.append(chunk)
        total += len(chunk)
    return "\n".join(parts)


def run_review(diff: str, ollama_url: str, api_key: str, model: str) -> str:
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    client = Client(host=ollama_url, headers=headers)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Please review this diff:\n\n```diff\n{diff}\n```"},
    ]
    response = client.chat(model=model, messages=messages)
    # ollama >= 0.4 returns an object; fall back to dict access for older versions
    try:
        return response.message.content
    except AttributeError:
        return response["message"]["content"]


def post_comment(repo, pr_number: int, body: str) -> None:
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(body)
    logger.info("Posted review comment to PR #%d", pr_number)


def main() -> None:
    github_token = os.environ["GITHUB_TOKEN"]
    repo_name = os.environ["GITHUB_REPOSITORY"]
    pr_number_str = os.environ.get("PR_NUMBER") or os.environ.get("GITHUB_PR_NUMBER")
    if not pr_number_str:
        logger.error("PR_NUMBER env var is required")
        sys.exit(1)
    pr_number = int(pr_number_str)

    ollama_url = os.environ.get("OLLAMA_CONTROL_PLANE_URL", "http://localhost:11434")
    api_key = os.environ.get("OLLAMA_API_KEY", "")
    model = os.environ.get("REVIEW_MODEL", "qwen3-coder:7b-q4")

    gh = Github(github_token)
    repo = gh.get_repo(repo_name)

    logger.info("Fetching diff for PR #%d in %s", pr_number, repo_name)
    diff = get_pr_diff(repo, pr_number)

    if not diff.strip():
        logger.info("Empty diff – skipping review")
        return

    logger.info("Running review with model %s (diff: %d chars)", model, len(diff))
    review = run_review(diff, ollama_url, api_key, model)

    comment_body = f"## 🤖 QReview\n> Reviewed by `{model}` via ollama-control-plane\n\n{review}"
    post_comment(repo, pr_number, comment_body)


if __name__ == "__main__":
    main()
