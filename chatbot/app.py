"""EC サイト向けハイブリッドチャットボット（デモ／プロトタイプ）。

処理の流れ:
  1. まず FAQ（ルールベース）で回答できるか判定し、できれば即答（API コスト不要）。
  2. FAQ で対応できなければ Claude API に商品データ・FAQ を渡して回答を生成。
  3. API キーが未設定の場合は AI フォールバックを無効化し、案内メッセージを返す
     （FAQ 部分だけでデモを起動できる）。
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from faq import FaqStore

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"

MODEL = "claude-opus-4-8"

app = FastAPI(title="EC Chatbot Demo")

faq_store = FaqStore()
products = json.loads((DATA_DIR / "products.json").read_text(encoding="utf-8"))

# anthropic SDK は API キーがある場合のみ初期化する（無くても FAQ は動く）。
_anthropic_client = None
if os.environ.get("ANTHROPIC_API_KEY"):
    try:
        import anthropic

        _anthropic_client = anthropic.Anthropic()
    except Exception:  # SDK 未インストールなど
        _anthropic_client = None


SYSTEM_PROMPT = """あなたは EC サイト「Example Store」のカスタマーサポート担当チャットボットです。

役割:
- お客様の質問に、丁寧で簡潔な日本語で回答してください。
- 下記の「商品情報」と「FAQ」を根拠に回答してください。
- 在庫状況（stock が 0 の場合は在庫切れ）や価格は商品情報を正確に反映してください。
- 情報が不足していて確実に答えられない場合は、推測で断定せず、
  サポート窓口（support@example.com / 0120-000-000 平日10:00〜18:00）への
  問い合わせを案内してください。
- 注文番号・住所・カード番号などの個人情報をこのチャットに入力しないよう必要に応じて注意してください。
"""


def build_context() -> str:
    """商品情報と FAQ をまとめたコンテキスト文字列を作る。"""
    product_lines = []
    for p in products:
        stock = "在庫切れ" if p["stock"] == 0 else f"在庫{p['stock']}点"
        product_lines.append(
            f"- [{p['id']}] {p['name']}（{p['category']}）"
            f" 価格{p['price']:,}円 / {stock}\n  {p['description']}"
        )
    products_text = "\n".join(product_lines)
    return f"# 商品情報\n{products_text}\n\n# FAQ\n{faq_store.as_context()}"


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    source: str  # "faq" | "ai" | "fallback"
    faq_id: str | None = None


def ai_reply(message: str) -> str:
    """Claude API で回答を生成する。"""
    response = _anthropic_client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=[
            {"type": "text", "text": SYSTEM_PROMPT},
            {
                "type": "text",
                "text": build_context(),
                "cache_control": {"type": "ephemeral"},
            },
        ],
        messages=[{"role": "user", "content": message}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    message = req.message.strip()
    if not message:
        return ChatResponse(reply="ご質問を入力してください。", source="fallback")

    # 1) FAQ で対応できるか
    match = faq_store.best_match(message)
    if match:
        return ChatResponse(reply=match.answer, source="faq", faq_id=match.faq_id)

    # 2) AI フォールバック
    if _anthropic_client is not None:
        try:
            return ChatResponse(reply=ai_reply(message), source="ai")
        except Exception:
            pass  # 失敗時は下の案内メッセージへ

    # 3) AI が使えない場合の案内
    return ChatResponse(
        reply=(
            "申し訳ありません、その質問にはまだ自動でお答えできません。"
            "お手数ですが support@example.com までお問い合わせください。"
        ),
        source="fallback",
    )


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
