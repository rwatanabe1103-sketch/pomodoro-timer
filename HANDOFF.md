# HANDOFF

- 更新: 2026-08-26 10:30 JST
- 更新者: Claude Code
- 対象Issue: なし（未作成）
- 作業ブランチ: claude/ai-collaboration-structure-261j0e
- PR: なし
- 状態: レビュー待ち

## いま何をしていたか
Codex との協働体制の初期構成を作成。AGENTS.md（ルール正本）、CLAUDE.md、HANDOFF.md、
.claude/skills/handoff、.agents/skills の symlink を新規追加した。

## 次にやること
- Codex 側で新規セッションを起動し、`.agents/skills` の symlink 経由で handoff スキルが認識されるか確認する
- 認識確認が取れたら、gyomu-tanaoroshi / product-info-tool へ同じ構成を横展開する
- 1往復の試験用に GitHub Issue を1件作成する

## 詰まっている点・人間の判断が必要な点
symlink 経由のスキル認識は未検証。Codex 側での確認結果待ち。
