# 📋 製品要件 (Python 版)

## 🎯 プロダクトビジョン
ollama-control-plane + Qwen3-Coder を使って、GitHub PR のコードレビューを自動化する Python スクリプトを提供する。

- ターゲットユーザー:
  - コードコメントを自動化したいチームリードや SRE。
  - Copilot Code Review のコストを下げたい中小企業。
- 核心価値:
  - コスト削減（GPU がある環境ならほぼ無料）。
  - 機密データ流出を抑える（ローカル / 自社サーバーで LLM を動かす）。
  - 社内コーディングルールやセキュリティチェックをプロンプトで定義・注入できる。

## ✅ 機能要件（MVP）
1. GitHub Actions から `pull_request` イベントを検知する。
2. 対象 PR の差分を取得し、一定バイト以内に切り詰める（長い diff への対策）。
3. `ollama-control-plane` の OpenAI 互換 API にリクエストを送信し、Qwen3-Coder によるレビューを行う。
4. レビュー結果を文字列として受け取り、PR にコメントとして投稿する。
5. 環境設定は `OLLAMA_CONTROL_PLANE_URL` と `OLLAMA_API_KEY` で切り替える。

## ❌ 非機能要件（MVP）
- 処理時間: 1 PR あたり平均 30 秒以内（7B 量子化モデル前提）。
- 信頼性: 基本的なエラー処理（ネットワークエラー、API エラー、空 diff 時）。
- 保守性:
  - Python 3.10 以上で動作確認。
  - linter（flake8/black）と単体テスト（pytest など）を CI で実行。

## 📊 成功指標（MVP）
- PR ごとに 1 件のレビューコメントが自動投稿されている。
- おおよそ 1 分以内にコメントが PR につく（人力-review と比べて目安 3 分以上短縮）。
- Copilot Code Review の利用を全体の 70% 以上削減できた。