# 🛫 QReview - Python 版

## 🚀 プロジェクト概要
ollama-control-plane を GitHub Actions で呼び、Python から Qwen3-Coder で PR 自動コードレビューを行うツール。
- 保守対象: Python (`review.py`) による実装
- 使用ライブラリ: `ollama`, `PyGithub`, `requests`
- 差別化: Copilot Code Review より安価・ローカル・カスタム規約対応。

## 📋 Claude Code での進め方
1. まず `docs/INDEX.md` を開く。
2. そのあと `docs/product-requirements.md` と `docs/architecture.md` を読む。
3. 実装前に `docs/spec-mvp-review-py.md` と `.github/workflows/qreview.yml` を確認・更新する。
4. テストについては `tests/` 配下に実装し、GitHub Actions または `act` で実行する。

## 🎯 今日のタスク例
- `docs/product-requirements.md` を Claude で読み直す
- `.github/workflows/qreview.yml` を作成・調整する
- `review.py` を実装し、ローカルで `ollama-control-plane` と連携させたテストを書く