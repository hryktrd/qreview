# QReview

GitHub PR の差分を **Qwen3-Coder**（[ollama-control-plane](https://github.com/hryktrd/ollama-control-plane) 経由）で自動レビューし、PR にコメントとして投稿するツールです。

---

## 仕組み

```
PR open/sync
    └─ GitHub Actions (qreview.yml)
            └─ review.py
                    ├─ PyGithub で PR diff 取得
                    ├─ ollama-control-plane (Qwen3-Coder) へリクエスト
                    └─ 結果を PR コメントとして投稿
```

---

## セットアップ

### 1. ollama-control-plane の準備

- ollama-control-plane を外部公開し、以下のモデルを事前に pull しておく。

```bash
ollama pull qwen3-coder:7b-q4
```

- エンドポイント例: `https://your-cp.example.com/v1`

### 2. このリポジトリへ組み込む

このリポジトリの `.github/workflows/qreview.yml` をレビュー対象のリポジトリにコピーし、`review.py` と `requirements.txt` も同梱します。

または、[テンプレートとして使う](#テンプレートとして使う) を参照してください。

### 3. GitHub Secrets / Variables の設定

対象リポジトリの **Settings → Secrets and variables → Actions** で以下を設定します。

| 種類 | 名前 | 値の例 |
|------|------|--------|
| Secret | `OLLAMA_CONTROL_PLANE_URL` | `https://your-cp.example.com/v1` |
| Secret | `OLLAMA_API_KEY` | APIキーまたはベアラートークン |
| Variable (任意) | `REVIEW_MODEL` | `qwen3-coder:7b-q4`（デフォルト） |

`GITHUB_TOKEN` は Actions が自動で提供するため設定不要です。

---

## 使い方

### 通常の使い方

セットアップ完了後は **PR を open または更新するだけ**で自動的にレビューが走ります。

レビュー結果は PR のコメント欄に以下の形式で投稿されます。

```
## 🤖 QReview
> Reviewed by `qwen3-coder:7b-q4` via ollama-control-plane

（レビュー内容）
```

### ローカルで手動実行

```bash
pip install -r requirements.txt

export GITHUB_TOKEN=ghp_xxxx
export GITHUB_REPOSITORY=owner/repo
export PR_NUMBER=42
export OLLAMA_CONTROL_PLANE_URL=http://localhost:11434
export OLLAMA_API_KEY=                   # ローカルなら空でOK
export REVIEW_MODEL=qwen3-coder:7b-q4

python review.py
```

### テンプレートとして使う

1. このリポジトリをフォークまたはテンプレートとして新規リポジトリを作成。
2. 対象リポジトリに以下のファイルをコピー。
   - `.github/workflows/qreview.yml`
   - `review.py`
   - `requirements.txt`
3. Secrets を設定して PR を作成するだけで動作します。

---

## 環境変数リファレンス

| 変数名 | 必須 | デフォルト | 説明 |
|--------|------|-----------|------|
| `GITHUB_TOKEN` | ✅ | — | PR コメント投稿権限 |
| `GITHUB_REPOSITORY` | ✅ | — | `owner/repo` 形式 |
| `PR_NUMBER` | ✅ | — | レビュー対象 PR 番号 |
| `OLLAMA_CONTROL_PLANE_URL` | ✅ | `http://localhost:11434` | ollama エンドポイント (`/v1` まで) |
| `OLLAMA_API_KEY` | — | `""` | Bearer トークン（ローカルは不要） |
| `REVIEW_MODEL` | — | `qwen3-coder:7b-q4` | 使用モデル名 |

---

## テスト

```bash
pip install -r requirements.txt
pytest tests/ -v
```

---

## ファイル構成

```
.
├── .github/
│   └── workflows/
│       └── qreview.yml   # GitHub Actions ワークフロー
├── docs/                 # 設計・仕様ドキュメント
├── tests/
│   └── test_review.py    # ユニットテスト
├── review.py             # メインスクリプト
├── requirements.txt
└── README.md
```

---

## カスタムレビュー規約

`review.py` 内の `SYSTEM_PROMPT` を編集することで、チーム固有のコーディング規約やセキュリティチェック項目を追加できます。

```python
SYSTEM_PROMPT = """\
You are an expert code reviewer. ...
追加ルール:
- 社内命名規則に従っているか確認する
- XXXライブラリの使用を禁止する
"""
```

---

## ライセンス

MIT
