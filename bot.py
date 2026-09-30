from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder


# ==================================================
# 設定
# ==================================================

# BotFatherで発行したBotトークンを入れてください
TOKEN = "8807013382:AAFxQzoFHFHOIRbsJv1oATwTMRH6oj5b70k"

# 管理者のTelegram ID
ADMIN_ID = 6833171461


# ==================================================
# Bot
# ==================================================

bot = Bot(token=TOKEN)
dp = Dispatcher()


# ==================================================
# 商品
# ==================================================

PRODUCTS = {
    "5000": ("🔥 即反映OLDアカウント", 5000),
    "3000": ("🔥 手押し最強アカウント", 3000),
    "1000": ("⚡ 即反映アカウント", 1000),
    "700": ("💰 格安即反映アカウント", 700),
}


# ==================================================
# 支払い待ち注文
# ==================================================

pending_orders = {}


# ==================================================
# /start
# ==================================================

@dp.message(CommandStart())
async def start(message: Message):

    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="🐦 Twitterアカウント",
        callback_data="twitter"
    )

    keyboard.adjust(1)

    await message.answer(
        "🛒 ショップへようこそ！\n\n"
        "購入したい商品を選択してください。",
        reply_markup=keyboard.as_markup()
    )


# ==================================================
# Twitter商品一覧
# ==================================================

@dp.callback_query(F.data == "twitter")
async def twitter_menu(callback: CallbackQuery):

    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="🔥 即反映OLDアカウント ¥5,000",
        callback_data="product:5000"
    )

    keyboard.button(
        text="🔥 手押し最強アカウント ¥3,000",
        callback_data="product:3000"
    )

    keyboard.button(
        text="⚡ 即反映アカウント ¥1,000",
        callback_data="product:1000"
    )

    keyboard.button(
        text="💰 格安即反映アカウント ¥700",
        callback_data="product:700"
    )

    keyboard.button(
        text="🏠 戻る",
        callback_data="home"
    )

    keyboard.adjust(1)

    await callback.message.edit_text(
        "🐦 Twitterアカウント\n\n"
        "購入したい商品を選択してください。",
        reply_markup=keyboard.as_markup()
    )

    await callback.answer()


# ==================================================
# 商品詳細
# ==================================================

@dp.callback_query(F.data.startswith("product:"))
async def product_detail(callback: CallbackQuery):

    product_id = callback.data.split(":")[1]

    if product_id not in PRODUCTS:
        await callback.answer(
            "❌ 商品が見つかりません。",
            show_alert=True
        )
        return

    name, price = PRODUCTS[product_id]

    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text=f"💳 購入する ¥{price:,}",
        callback_data=f"buy:{product_id}"
    )

    keyboard.button(
        text="🔙 商品一覧",
        callback_data="twitter"
    )

    keyboard.adjust(1)

    await callback.message.edit_text(
        f"{name}\n\n"
        f"💴 価格：{price:,}円\n\n"
        "購入する場合は下のボタンを押してください。",
        reply_markup=keyboard.as_markup()
    )

    await callback.answer()


# ==================================================
# 購入ボタン
# ==================================================

@dp.callback_query(F.data.startswith("buy:"))
async def buy(callback: CallbackQuery):

    product_id = callback.data.split(":")[1]

    if product_id not in PRODUCTS:
        await callback.answer(
            "❌ 商品が見つかりません。",
            show_alert=True
        )
        return

    name, price = PRODUCTS[product_id]

    user_id = callback.from_user.id

    # 注文を保存
    pending_orders[user_id] = {
        "product": name,
        "price": price,
    }

    await callback.message.answer(
        "🧾 ご注文内容\n"
        "━━━━━━━━━━━━\n\n"
        f"📦 商品：{name}\n"
        f"💴 金額：{price:,}円\n\n"
        "━━━━━━━━━━━━\n"
        "💳 PayPayでお支払いください\n"
        "━━━━━━━━━━━━\n\n"
        f"⚠️ 必ず {price:,}円 を送金してください。\n\n"
        "支払い後、PayPayの送金リンクを\n"
        "このBotに送ってください。\n\n"
        "例：\n"
        "https://pay.paypay.ne.jp/xxxxxxxx"
    )

    await callback.answer()


# ==================================================
# PayPay送金リンク受付
# ==================================================

@dp.message()
async def receive_paypay_link(message: Message):

    user_id = message.from_user.id

    # 購入手続き中でない場合
    if user_id not in pending_orders:

        await message.answer(
            "⚠️ 先に /start から商品を選択してください。"
        )

        return

    # テキスト以外
    if not message.text:

        await message.answer(
            "❌ PayPay送金リンクを送ってください。"
        )

        return

    link = message.text.strip()

    # PayPayリンク確認
    if not link.startswith("https://pay.paypay.ne.jp/"):

        await message.answer(
            "❌ PayPay送金リンクが正しくありません。\n\n"
            "PayPayアプリから送金リンクをコピーして、"
            "そのままBotへ送ってください。"
        )

        return

    order = pending_orders[user_id]

    product = order["product"]
    price = order["price"]


    # ==================================================
    # 管理者用認証ボタン
    # ==================================================

    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="✅ 入金を認証する",
        callback_data=f"approve:{user_id}"
    )

    keyboard.adjust(1)


    # ==================================================
    # 管理者へ送信
    # ==================================================

    await bot.send_message(

        ADMIN_ID,

        "🔔 新しい支払い報告\n"
        "━━━━━━━━━━━━\n\n"

        f"👤 ユーザー：{message.from_user.full_name}\n"
        f"🆔 Telegram ID：{user_id}\n\n"

        f"📦 商品：{product}\n"
        f"💴 注文金額：{price:,}円\n\n"

        f"💳 PayPay送金リンク：\n"
        f"{link}\n\n"

        "━━━━━━━━━━━━\n"
        "⚠️ PayPayアプリで実際の入金を確認してから\n"
        "下の認証ボタンを押してください。",

        reply_markup=keyboard.as_markup()
    )


    # ==================================================
    # 購入者へ返信
    # ==================================================

    await message.answer(

        "✅ PayPay送金リンクを受け付けました。\n\n"

        f"📦 商品：{product}\n"
        f"💴 注文金額：{price:,}円\n\n"

        "管理者へ送信しました。\n\n"

        "⏳ 入金確認をお待ちください。"
    )


# ==================================================
# 管理者「認証する」
# ==================================================

@dp.callback_query(F.data.startswith("approve:"))
async def approve_payment(callback: CallbackQuery):

    # 管理者チェック
    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "❌ 管理者専用です。",
            show_alert=True
        )

        return


    # ユーザーID取得
    try:

        user_id = int(
            callback.data.split(":")[1]
        )

    except (ValueError, IndexError):

        await callback.answer(
            "❌ 注文情報が正しくありません。",
            show_alert=True
        )

        return


    # 注文が存在するか確認
    if user_id not in pending_orders:

        await callback.answer(
            "⚠️ この注文は存在しないか、すでに処理されています。",
            show_alert=True
        )

        return


    order = pending_orders[user_id]

    product = order["product"]
    price = order["price"]


    # ==================================================
    # 購入者へ認証通知
    # ==================================================

    try:

        await bot.send_message(

            user_id,

            "✅ 入金確認済み\n"
            "━━━━━━━━━━━━\n\n"

            f"📦 商品：{product}\n"
            f"💴 金額：{price:,}円\n\n"

            "管理者による入金確認が完了しました。\n"
            "商品の案内をお待ちください。"
        )

    except Exception:

        pass


    # ==================================================
    # 管理者側を認証済みに変更
    # ==================================================

    try:

        await callback.message.edit_text(

            callback.message.text +

            "\n\n"
            "━━━━━━━━━━━━\n"
            "✅ 入金認証済み\n"
            f"👨‍💼 認証者：{callback.from_user.full_name}"

        )

    except Exception:

        pass


    # 注文削除
    del pending_orders[user_id]


    await callback.answer(
        "✅ 入金を認証しました。"
    )


# ==================================================
# ホーム
# ==================================================

@dp.callback_query(F.data == "home")
async def home(callback: CallbackQuery):

    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="🐦 Twitterアカウント",
        callback_data="twitter"
    )

    keyboard.adjust(1)

    await callback.message.edit_text(

        "🛒 ショップへようこそ！\n\n"
        "購入したい商品を選択してください。",

        reply_markup=keyboard.as_markup()
    )

    await callback.answer()


# ==================================================
# Bot起動
# ==================================================

async def main():

    print("🤖 Bot起動中...")

    await dp.start_polling(bot)


# ==================================================
# Google Colab用
# ==================================================

await main()
