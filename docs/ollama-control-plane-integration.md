# 🔌 ollama-control-plane との連携（Python 版）

## 📦 事前準備
- 下記 URL で ollama-control-plane を公開していること。
  - 例: `https://your-cp.example.com/v1/chat/completions`
- 以下モデルを事前 pull:
  - `ollama pull qwen3-coder:7b-q4`
- GitHub リポジトリの Secrets に以下を設定:
  - `OLLAMA_CONTROL_PLANE_URL` – `https://your-cp.example.com/v1`
  - `OLLAMA_API_KEY` – API キーまたはベアラートークン値

## 🧪 Python での連携手順（ollama ライブラリ）

1. 依存をインストール:
   ```bash
   pip install ollama
   ```
2. Python でクライアントを初期化:
   ```python
   from ollama import Client

   client = Client(host=OLLAMA_CONTROL_PLANE_URL)
   ```
3. チャットリクエスト:
   ```python
   messages = [
       {"role": "system", "content": "TypeScript/React 用のコーディング規約を守ってレビューします。……"},
       {"role": "user", "content": f"Review this diff:\n```diff\n{diff}\n```"},
   ]
   response = client.chat(model="qwen3-coder:7b-q4", messages=messages, options={})
   content = response["message"]["content"]
   ```
4. GitHub へコメント投稿:
   - `PyGithub` を使って `pull_request.create_comment(...)` などで `content` を投稿する。

## ⚠️ 注意点
- ローカル環境でテストする場合は、`OLLAMA_CONTROL_PLANE_URL` を `http://localhost:11434/v1` などにする。
- コメント投稿に失敗した場合のリトライ処理や、ログ出力を入れておくと運用性が上がる。