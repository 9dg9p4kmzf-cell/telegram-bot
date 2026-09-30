import os

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import (
    Update,
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.filters import CommandStart


# ==========================================
# 設定
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

PRODUCT_NAME = "商品"
PRODUCT_PRICE = 4000


# ==========================================
# Bot
# ==========================================

if not BOT_TOKEN: "8807013382:AAE_ajvbvIIMgh34ue7skgRUvy5gNRRxtH0"
    raise RuntimeError("BOT_TOKEN が設定されていません")

if ADMIN_ID == 0:6833171461
    raise RuntimeError("ADMIN_ID が設定されていません")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()


# ==========================================
# /start
# ==========================================

@dp.message(CommandStart())
async def start(message: Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"🛒 {PRODUCT_PRICE}円で購入",
                    callback_data="buy"
                )
            ]
        ]
    )

    await message.answer(
        f"🛍 {PRODUCT_NAME}\n\n"
        f"💰 価格：{PRODUCT_PRICE}円\n\n"
        "購入する場合は下のボタンを押してください。",
        reply_markup=keyboard
    )


# ==========================================
# 購入ボタン
# ==========================================

@dp.callback_query(lambda c: c.data == "buy")
async def buy(callback: CallbackQuery):

    await callback.answer()

    await callback.message.answer(
        "💰 お支払い\n\n"
        f"商品価格：{PRODUCT_PRICE}円\n\n"
        "PayPayで支払い後、"
        "このチャットにPayPay送金リンクを送ってください。\n\n"
        "例：\n"
        "https://pay.paypay.ne.jp/xxxxxxxx"
    )


# ==========================================
# PayPayリンク受信
# ==========================================

@dp.message(
    lambda message:
    message.text is not None
    and "pay.paypay.ne.jp" in message.text
)
async def receive_paypay(message: Message):

    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "ユーザー名なし"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ 承認",
                    callback_data=f"approve:{message.from_user.id}"
                ),
                InlineKeyboardButton(
                    text="❌ 却下",
                    callback_data=f"reject:{message.from_user.id}"
                )
            ]
        ]
    )

    await bot.send_message(
        ADMIN_ID,
        "🔔 支払い申請\n\n"
        f"👤 ユーザー：{username}\n"
        f"🆔 ID：{message.from_user.id}\n"
        f"💰 金額：{PRODUCT_PRICE}円\n\n"
        f"🔗 PayPayリンク：\n{message.text}\n\n"
        "⚠️ 実際の支払いを確認してから操作してください。",
        reply_markup=keyboard
    )

    await message.answer(
        "✅ PayPayリンクを受け付けました。\n\n"
        "管理者が支払いを確認しています。"
    )


# ==========================================
# 承認
# ==========================================

@dp.callback_query(
    lambda c:
    c.data is not None
    and c.data.startswith("approve:")
)
async def approve(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "管理者のみ操作できます。",
            show_alert=True
        )
        return

    user_id = int(callback.data.split(":")[1])

    await bot.send_message(
        user_id,
        "✅ 支払いが承認されました！\n\n"
        "ご購入ありがとうございます。\n"
        "商品の受け取りについては管理者から案内します。"
    )

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.answer("承認しました")


# ==========================================
# 却下
# ==========================================

@dp.callback_query(
    lambda c:
    c.data is not None
    and c.data.startswith("reject:")
)
async def reject(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "管理者のみ操作できます。",
            show_alert=True
        )
        return

    user_id = int(callback.data.split(":")[1])

    await bot.send_message(
        user_id,
        "❌ 支払いを確認できませんでした。\n\n"
        "もう一度ご確認ください。"
    )

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.answer("却下しました")


# ==========================================
# Render確認用
# ==========================================

@app.get("/")
async def home():
    return {
        "status": "online",
        "bot": "telegram-bot"
    }


# ==========================================
# Telegram Webhook
# ==========================================

@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    update = Update.model_validate(data)

    await dp.feed_update(
        bot,
        update
    )

    return {"ok": True}


# ==========================================
# 起動時
# ==========================================

@app.on_event("startup")
async def startup():

    if not RENDER_URL:
        raise RuntimeError(
            "RENDER_EXTERNAL_URL が設定されていません"
        )

    webhook_url = f"{RENDER_URL}/webhook"

    await bot.set_webhook(
        url=webhook_url,
        drop_pending_updates=True
    )

    print("================================")
    print("Telegram Bot Started")
    print(f"Webhook: {webhook_url}")
    print("================================")


# ==========================================
# 終了時
# ==========================================

@app.on_event("shutdown")
async def shutdown():

    await bot.delete_webhook()
    await bot.session.close()