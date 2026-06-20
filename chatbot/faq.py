"""FAQ（ルールベース）マッチング。

ユーザーの質問にキーワードが多く含まれる FAQ を探し、十分なスコアがあれば
即答する。スコアが低ければ None を返し、呼び出し側で AI フォールバックに回す。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


@dataclass
class FaqMatch:
    faq_id: str
    question: str
    answer: str
    score: int


class FaqStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (DATA_DIR / "faq.json")
        self.entries: list[dict] = json.loads(self.path.read_text(encoding="utf-8"))

    def best_match(self, message: str) -> FaqMatch | None:
        """メッセージに最もマッチする FAQ を返す。なければ None。"""
        text = message.lower()
        best: FaqMatch | None = None

        for entry in self.entries:
            score = sum(1 for kw in entry["keywords"] if kw.lower() in text)
            if score == 0:
                continue
            if best is None or score > best.score:
                best = FaqMatch(
                    faq_id=entry["id"],
                    question=entry["question"],
                    answer=entry["answer"],
                    score=score,
                )

        # キーワードが1つ以上ヒットしたら FAQ で回答する
        if best and best.score >= 1:
            return best
        return None

    def as_context(self) -> str:
        """AI フォールバック時に渡す FAQ 一覧（参照用テキスト）。"""
        lines = []
        for entry in self.entries:
            lines.append(f"Q: {entry['question']}\nA: {entry['answer']}")
        return "\n\n".join(lines)
