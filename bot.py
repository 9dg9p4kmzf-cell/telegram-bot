import os
import asyncio

from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
import uvicorn


# =========================
# 設定
# =========================

BOT_TOKEN = os.getenv("8807013382:AAFxQzoFHFHOIRbsJv1oATwTMRH6oj5b70k")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN が設定されていません")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()


# =========================
# Telegram
# =========================

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🤖 ボットが起動しています！\n\n"
        "メニューから商品を選択できます。"
    )


@dp.message()
async def message_handler(message: Message):
    await message.answer(
        "メッセージを受け取りました。\n"
        "/start でメニューを表示できます。"
    )


# =========================
# Bot起動
# =========================

async def start_bot():
    await dp.start_polling(bot)


@app.on_event("startup")
async def startup():
    asyncio.create_task(start_bot())


@app.get("/")
async def home():
    return {"status": "running", "bot": "online"}


# =========================
# Render
# =========================

if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )