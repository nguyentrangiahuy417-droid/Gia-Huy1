"""
=============================================================
  GAME KEY SHOP — Telegram Bot
  bot.py  |  python-telegram-bot v20+
=============================================================
  Cài thư viện:
      pip install python-telegram-bot==20.7

  Chạy:
      python bot.py

  Cấu hình:
      Sửa BOT_TOKEN và ADMIN_ID bên dưới
=============================================================
"""

import json
import logging
import os
import asyncio
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ─────────────────────────────────────────────────────────
#  ⚙️  CẤU HÌNH — đọc từ biến môi trường (Railway / Render / systemd)
#  KHÔNG hardcode token vào đây — đặt trong Railway Dashboard → Variables
# ─────────────────────────────────────────────────────────
BOT_TOKEN  = os.environ.get("BOT_TOKEN", "")
ADMIN_ID   = int(os.environ.get("ADMIN_ID", "0"))
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://nguyentrangiahuy417-droid.github.io/game-key-shop/")

# Thông tin thanh toán hiển thị cho khách
PAYMENT_INFO = """
💳 <b>Thông tin thanh toán:</b>

🏦 <b>MoMo:</b> 0901234567 (Nguyễn Văn A)
🏦 <b>Banking:</b> MB Bank - 12345678901 - NGUYEN VAN A
🏦 <b>USDT (TRC20):</b> TXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

📸 Chụp màn hình chuyển khoản và gửi vào đây
⏰ Key sẽ được gửi trong vòng <b>5–15 phút</b>
"""

# ─────────────────────────────────────────────────────────
#  📦  KHO KEY (thay bằng database thực tế sau)
#  Format: "Tên game|Loại": ["KEY1", "KEY2", ...]
# ─────────────────────────────────────────────────────────
KEY_STOCK: dict[str, list[str]] = {
    "Elden Ring|Standard Edition":          ["XXXXX-XXXXX-XXXXX-ELDEN1", "XXXXX-XXXXX-XXXXX-ELDEN2"],
    "Elden Ring|Deluxe Edition":            ["DELUX-XXXXX-XXXXX-ELD01"],
    "GTA V + Online|Standard":              ["GTAV5-XXXXX-XXXXX-STD01", "GTAV5-XXXXX-XXXXX-STD02"],
    "GTA V + Online|Premium":               ["GTAV5-XXXXX-XXXXX-PREM1"],
    "Cyberpunk 2077|Base Game":             ["CYBPK-XXXXX-XXXXX-BASE1"],
    "Cyberpunk 2077|Ultimate Edition (+DLC)":["CYBPK-XXXXX-XXXXX-ULT01"],
    "FIFA 25|Standard":                     ["FIFA25-XXXX-XXXXX-STD01"],
    "FIFA 25|Ultimate":                     ["FIFA25-XXXX-XXXXX-ULT01"],
    "Minecraft Java|Java Edition":          ["MCJVA-XXXXX-XXXXX-JAVA1"],
    "Minecraft Java|Java + Bedrock Bundle": ["MCJVA-XXXXX-XXXXX-BDL01"],
    "Hogwarts Legacy|Standard":             ["HOGWT-XXXXX-XXXXX-STD01"],
    "Hogwarts Legacy|Deluxe":               ["HOGWT-XXXXX-XXXXX-DLX01"],
}

# ─────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

# Lưu đơn hàng đang chờ xác nhận {user_id: order_data}
pending_orders: dict[int, dict] = {}


# ═══════════════════════════════════════════════════════════
#  LỆNH /start
# ═══════════════════════════════════════════════════════════
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "🎮  Vào cửa hàng",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]])
    await update.message.reply_html(
        f"👋 Xin chào <b>{user.first_name}</b>!\n\n"
        "🎮 <b>Game Key Shop</b> — Mua key game giá tốt nhất\n\n"
        "✅ Key chính hãng, giao ngay sau thanh toán\n"
        "💬 Hỗ trợ 24/7 qua chat\n\n"
        "Nhấn nút bên dưới để xem cửa hàng 👇",
        reply_markup=keyboard,
    )


# ═══════════════════════════════════════════════════════════
#  LỆNH /stock  (admin xem kho)
# ═══════════════════════════════════════════════════════════
async def cmd_stock(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Chỉ admin mới dùng được lệnh này.")
        return

    lines = ["📦 <b>Tồn kho hiện tại:</b>\n"]
    for key, keys in KEY_STOCK.items():
        game, edition = key.split("|", 1)
        stock = len(keys)
        icon = "🟢" if stock > 2 else ("🟡" if stock > 0 else "🔴")
        lines.append(f"{icon} <b>{game}</b> — {edition}: <code>{stock} key</code>")

    await update.message.reply_html("\n".join(lines))


# ═══════════════════════════════════════════════════════════
#  LỆNH /addkey  (admin thêm key vào kho)
#  Cú pháp: /addkey Elden Ring|Standard Edition|KEY1-KEY2-KEY3
# ═══════════════════════════════════════════════════════════
async def cmd_addkey(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Chỉ admin mới dùng được lệnh này.")
        return

    try:
        args = " ".join(ctx.args)
        parts = args.split("|")
        if len(parts) != 3:
            raise ValueError

        game, edition, new_key = parts[0].strip(), parts[1].strip(), parts[2].strip()
        stock_key = f"{game}|{edition}"

        if stock_key not in KEY_STOCK:
            KEY_STOCK[stock_key] = []
        KEY_STOCK[stock_key].append(new_key)

        await update.message.reply_html(
            f"✅ Đã thêm key vào kho:\n"
            f"🎮 <b>{game}</b> — {edition}\n"
            f"🔑 <code>{new_key}</code>\n"
            f"📦 Tổng còn: <b>{len(KEY_STOCK[stock_key])} key</b>"
        )
    except Exception:
        await update.message.reply_html(
            "❌ Cú pháp sai. Dùng:\n"
            "<code>/addkey Tên game|Loại edition|KEY-CODE-HERE</code>\n\n"
            "Ví dụ:\n"
            "<code>/addkey Elden Ring|Standard Edition|ABCDE-FGHIJ-KLMNO</code>"
        )


# ═══════════════════════════════════════════════════════════
#  NHẬN ĐƠN HÀNG TỪ WEB APP (web_app_data)
# ═══════════════════════════════════════════════════════════
async def handle_webapp_data(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    raw  = update.message.web_app_data.data

    try:
        order = json.loads(raw)
    except json.JSONDecodeError:
        await update.message.reply_text("❌ Lỗi dữ liệu đơn hàng. Vui lòng thử lại.")
        return

    if order.get("type") != "order" or not order.get("items"):
        await update.message.reply_text("❌ Đơn hàng không hợp lệ.")
        return

    # Lưu đơn chờ xác nhận
    pending_orders[user.id] = {
        "user_id":   user.id,
        "username":  user.username or user.first_name,
        "items":     order["items"],
        "total":     order["total"],
        "time":      datetime.now().strftime("%H:%M %d/%m/%Y"),
    }

    # Format đơn hàng đẹp
    items_text = "\n".join(
        f"  • 🎮 <b>{i['game']}</b> ({i['type']}): <code>{_fmt(i['price'])}</code>"
        for i in order["items"]
    )

    # Gửi thông tin thanh toán cho khách
    await update.message.reply_html(
        f"🛒 <b>Đơn hàng của bạn:</b>\n\n"
        f"{items_text}\n\n"
        f"💰 <b>Tổng cộng: {_fmt(order['total'])}</b>\n\n"
        f"{PAYMENT_INFO}",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Tôi đã chuyển khoản", callback_data="confirm_paid"),
            InlineKeyboardButton("❌ Huỷ đơn",            callback_data="cancel_order"),
        ]])
    )

    # Thông báo cho admin
    await ctx.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"🔔 <b>ĐƠN HÀNG MỚI!</b>\n\n"
            f"👤 User: <a href='tg://user?id={user.id}'>{user.first_name}</a>"
            f" (@{user.username or 'N/A'}) | ID: <code>{user.id}</code>\n\n"
            f"{items_text}\n\n"
            f"💰 <b>Tổng: {_fmt(order['total'])}</b>\n"
            f"🕐 Lúc: {pending_orders[user.id]['time']}"
        ),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(
                f"✅ Duyệt & gửi key → {user.first_name}",
                callback_data=f"approve_{user.id}"
            ),
        ]])
    )

    log.info(f"New order from {user.id} ({user.username}): {order['items']}")


# ═══════════════════════════════════════════════════════════
#  CALLBACK: Khách bấm "Đã chuyển khoản" / "Huỷ"
# ═══════════════════════════════════════════════════════════
async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data    = query.data

    # ── Khách xác nhận đã thanh toán ──
    if data == "confirm_paid":
        order = pending_orders.get(user_id)
        if not order:
            await query.edit_message_text("⚠️ Không tìm thấy đơn hàng. Vui lòng đặt lại.")
            return

        await query.edit_message_text(
            "⏳ Cảm ơn! Chúng tôi đang kiểm tra thanh toán của bạn.\n"
            "🔑 Key sẽ được gửi trong <b>5–15 phút</b>.\n\n"
            "Nếu quá thời gian, vui lòng nhắn /support",
            parse_mode="HTML"
        )

        # Nhắc admin
        await ctx.bot.send_message(
            ADMIN_ID,
            f"💸 <b>Khách xác nhận đã thanh toán!</b>\n"
            f"👤 User ID: <code>{user_id}</code> — {order['username']}\n"
            f"💰 {_fmt(order['total'])}\n\n"
            f"👉 Kiểm tra ví rồi bấm Duyệt để gửi key.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    f"✅ Duyệt & gửi key → {order['username']}",
                    callback_data=f"approve_{user_id}"
                ),
            ]])
        )

    # ── Khách huỷ đơn ──
    elif data == "cancel_order":
        pending_orders.pop(user_id, None)
        await query.edit_message_text("❌ Đơn hàng đã được huỷ. Nhấn /start để đặt lại.")

    # ── Admin duyệt đơn & gửi key ──
    elif data.startswith("approve_"):
        if query.from_user.id != ADMIN_ID:
            await query.answer("Chỉ admin mới dùng được!", show_alert=True)
            return

        target_user_id = int(data.split("_")[1])
        order = pending_orders.get(target_user_id)

        if not order:
            await query.edit_message_text("⚠️ Đơn hàng không tồn tại hoặc đã được xử lý.")
            return

        # Lấy key từ kho
        keys_sent  = []
        keys_out   = []

        for item in order["items"]:
            stock_key = f"{item['game']}|{item['type']}"
            if stock_key in KEY_STOCK and KEY_STOCK[stock_key]:
                key_code = KEY_STOCK[stock_key].pop(0)  # Lấy key đầu tiên
                keys_sent.append((item["game"], item["type"], key_code))
            else:
                keys_out.append(f"{item['game']} — {item['type']}")

        # Gửi key cho khách
        if keys_sent:
            key_lines = "\n".join(
                f"🎮 <b>{g}</b> ({t})\n🔑 <code>{k}</code>"
                for g, t, k in keys_sent
            )
            await ctx.bot.send_message(
                target_user_id,
                f"✅ <b>Thanh toán xác nhận!</b> Đây là key của bạn:\n\n"
                f"{key_lines}\n\n"
                f"📋 Copy key và kích hoạt trên Steam/platform tương ứng.\n"
                f"💬 Nếu có vấn đề, nhắn /support",
                parse_mode="HTML"
            )

        # Thông báo nếu hết key
        if keys_out:
            out_text = "\n".join(f"• {x}" for x in keys_out)
            await ctx.bot.send_message(
                target_user_id,
                f"⚠️ Một số sản phẩm hiện đang hết hàng:\n{out_text}\n\n"
                f"Chúng tôi sẽ bổ sung sớm và liên hệ lại!",
            )
            await query.message.reply_text(
                f"⚠️ Hết key cho:\n{out_text}\nHãy /addkey thêm vào kho!",
                parse_mode="HTML"
            )

        # Xoá đơn khỏi pending
        pending_orders.pop(target_user_id, None)

        await query.edit_message_text(
            f"✅ Đã gửi key cho user <code>{target_user_id}</code> ({order['username']})\n"
            f"📦 {len(keys_sent)} key đã gửi"
            + (f", {len(keys_out)} hết hàng" if keys_out else ""),
            parse_mode="HTML"
        )

        log.info(f"Admin approved order for {target_user_id}: {keys_sent}")


# ═══════════════════════════════════════════════════════════
#  LỆNH /support
# ═══════════════════════════════════════════════════════════
async def cmd_support(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        "💬 <b>Hỗ trợ khách hàng</b>\n\n"
        "Mô tả vấn đề của bạn và admin sẽ phản hồi sớm nhất.\n"
        "⏰ Thời gian hỗ trợ: 8:00 – 23:00 hàng ngày"
    )
    # Forward message tiếp theo của user đến admin
    ctx.user_data["awaiting_support"] = True


async def handle_support_msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Forward tin nhắn hỗ trợ đến admin."""
    if not ctx.user_data.get("awaiting_support"):
        return
    user = update.effective_user
    await ctx.bot.send_message(
        ADMIN_ID,
        f"📩 <b>Tin nhắn hỗ trợ từ:</b>\n"
        f"👤 {user.first_name} (@{user.username or 'N/A'}) | ID: <code>{user.id}</code>\n\n"
        f"💬 {update.message.text}\n\n"
        f"Trả lời: /reply_{user.id} &lt;nội dung&gt;",
        parse_mode="HTML"
    )
    await update.message.reply_text("✅ Đã gửi! Admin sẽ phản hồi sớm nhất có thể.")
    ctx.user_data["awaiting_support"] = False


# ─────────────────────────────────────────────────────────
def _fmt(n: int | float) -> str:
    """Format số tiền kiểu VN."""
    return f"{int(n):,}₫".replace(",", ".")


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start",   cmd_start))
    app.add_handler(CommandHandler("stock",   cmd_stock))
    app.add_handler(CommandHandler("addkey",  cmd_addkey))
    app.add_handler(CommandHandler("support", cmd_support))

    # WebApp data (đơn hàng từ Web App)
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))

    # Tin nhắn hỗ trợ (text thường từ user)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_support_msg))

    # Callback buttons (admin duyệt / khách xác nhận)
    app.add_handler(CallbackQueryHandler(handle_callback))

    log.info("🤖 Bot đang chạy...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
