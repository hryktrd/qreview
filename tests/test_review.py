"""Unit tests for review.py."""
from unittest.mock import MagicMock, patch

import pytest

import review


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_file(filename: str, patch_text: str):
    f = MagicMock()
    f.filename = filename
    f.patch = patch_text
    return f


def _make_pr(files):
    pr = MagicMock()
    pr.get_files.return_value = files
    return pr


def _make_repo(pr):
    repo = MagicMock()
    repo.get_pull.return_value = pr
    return repo


# ---------------------------------------------------------------------------
# get_pr_diff
# ---------------------------------------------------------------------------

class TestGetPrDiff:
    def test_single_file(self):
        pr = _make_pr([_make_file("foo.py", "@@ -1 +1 @@\n-old\n+new\n")])
        repo = _make_repo(pr)
        diff = review.get_pr_diff(repo, 42)
        assert "foo.py" in diff
        assert "+new" in diff

    def test_truncates_large_diff(self):
        big_patch = "+" + "x" * (review.MAX_DIFF_CHARS + 500)
        pr = _make_pr([_make_file("big.py", big_patch)])
        repo = _make_repo(pr)
        diff = review.get_pr_diff(repo, 1)
        assert len(diff) <= review.MAX_DIFF_CHARS

    def test_empty_patch_skipped(self):
        pr = _make_pr([_make_file("empty.py", None)])
        repo = _make_repo(pr)
        diff = review.get_pr_diff(repo, 1)
        assert "empty.py" in diff

    def test_multiple_files(self):
        files = [_make_file("a.py", "+a\n"), _make_file("b.py", "+b\n")]
        pr = _make_pr(files)
        repo = _make_repo(pr)
        diff = review.get_pr_diff(repo, 1)
        assert "a.py" in diff
        assert "b.py" in diff


# ---------------------------------------------------------------------------
# run_review
# ---------------------------------------------------------------------------

class TestRunReview:
    def _mock_openai_response(self, content: str):
        msg = MagicMock()
        msg.content = content
        choice = MagicMock()
        choice.message = msg
        resp = MagicMock()
        resp.choices = [choice]
        return resp

    @patch("review.OpenAI")
    def test_sends_correct_messages(self, MockOpenAI):
        instance = MockOpenAI.return_value
        instance.chat.completions.create.return_value = self._mock_openai_response("LGTM")

        result = review.run_review("diff text", "https://ocp.example.com/v1", "key123", "qwen2.5-coder:14b")

        MockOpenAI.assert_called_once_with(base_url="https://ocp.example.com/v1", api_key="key123")
        call_kwargs = instance.chat.completions.create.call_args.kwargs
        assert any("diff text" in m["content"] for m in call_kwargs["messages"])
        assert result == "LGTM"

    @patch("review.OpenAI")
    def test_empty_key_uses_none_placeholder(self, MockOpenAI):
        instance = MockOpenAI.return_value
        instance.chat.completions.create.return_value = self._mock_openai_response("ok")

        review.run_review("d", "https://ocp.example.com/v1", "", "model")

        MockOpenAI.assert_called_once_with(base_url="https://ocp.example.com/v1", api_key="none")


# ---------------------------------------------------------------------------
# post_comment
# ---------------------------------------------------------------------------

class TestPostComment:
    def test_creates_issue_comment(self):
        pr = MagicMock()
        repo = _make_repo(pr)
        review.post_comment(repo, 7, "Nice code!")
        pr.create_issue_comment.assert_called_once_with("Nice code!")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

class TestMain:
    _base_env = {
        "GITHUB_TOKEN": "tok",
        "GITHUB_REPOSITORY": "org/repo",
        "PR_NUMBER": "3",
        "OLLAMA_CONTROL_PLANE_URL": "https://ocp.example.com/v1",
        "OLLAMA_API_KEY": "secret",
        "REVIEW_MODEL": "qwen2.5-coder:14b",
    }

    @patch("review.post_comment")
    @patch("review.run_review", return_value="Looks good")
    @patch("review.get_pr_diff", return_value="diff content")
    @patch("review.github")
    def test_happy_path(self, mock_github, mock_diff, mock_review, mock_post, monkeypatch):
        for k, v in self._base_env.items():
            monkeypatch.setenv(k, v)

        review.main()

        mock_diff.assert_called_once()
        mock_review.assert_called_once()
        mock_post.assert_called_once()
        body = mock_post.call_args.args[2]
        assert "QReview" in body
        assert "Looks good" in body

    @patch("review.post_comment")
    @patch("review.run_review")
    @patch("review.get_pr_diff", return_value="   ")
    @patch("review.github")
    def test_skips_empty_diff(self, mock_github, mock_diff, mock_review, mock_post, monkeypatch):
        for k, v in self._base_env.items():
            monkeypatch.setenv(k, v)

        review.main()

        mock_review.assert_not_called()
        mock_post.assert_not_called()

    def test_missing_pr_number_exits(self, monkeypatch):
        for k, v in self._base_env.items():
            monkeypatch.setenv(k, v)
        monkeypatch.delenv("PR_NUMBER")

        with pytest.raises(SystemExit):
            review.main()
