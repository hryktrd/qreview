# 🧩 MVP 実装仕様（Python 版 review.py）

## 📁 構成
- ルート
  - `.github/workflows/qreview.yml`
  - `review.py`
  - `requirements.txt`
- docs/：既存ドキュメント
- tests/：テスト用 Python モジュール

## 📝 `.github/workflows/qreview.yml` 内容（概要）
- イベント: `pull_request` の `opened` / `synchronize` に対応。
- ジョブ: Python 3.12 を利用し、`requirements.txt` インストール後に `review.py` を実行。
- 必要な環境変数:
  - `OLLAMA_CONTROL_PLANE_URL`
  - `OLLAMA_API_KEY`（API 認証）
  - `GITHUB_TOKEN`

## 📝 `review.py` の責務
1. 環境変数を読み込み、GitHub と ollama に関する設定を確認する。
2. PR の差分を `git diff` で取得し、文字数制限をかける。
3. `ollama.chat` を用いて、以下のようなメッセージを送信する。
   - role: `system` – コーディング規約・チェック項目（可読性、セキュリティなど）。
   - role: `user` – 取得した diff を入れたコードレビュー要求。
4. 応答からレビュー本文を抽出し、GitHub PR にコメントとして投稿する。
5. 1 つの関数（例: `main()`）から実行できるようにし、`if __name__ == "__main__":` で呼び出す。

## 📝 `requirements.txt` の例
- 必須ライブラリ:
  - `ollama`
  - `PyGithub`
- 任意（ローカルテスト用）:
  - `pytest`
  - `requests`