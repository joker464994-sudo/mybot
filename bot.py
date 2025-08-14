# bot.py
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# -------- تنظیمات --------
TOKENS = [os.environ.get(f"TOKEN{i}") for i in range(1, 12) if os.environ.get(f"TOKEN{i}")]
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # آدرس هاستت
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
ADMINS = set([ADMIN_ID])

bot_on = True
group_id = None
timer_seconds = 1
fosh_list = []
fosh_mode = False
mention_user_id = None


# -------- هندل پیام --------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_on, group_id, timer_seconds, fosh_list, fosh_mode, mention_user_id, ADMINS

    if not update.message:
        return

    text = update.message.text.strip()
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    is_owner = (user_id == ADMIN_ID)
    is_admin = (user_id in ADMINS)

    if not is_admin:
        print(f"[BLOCKED] User {user_id} tried: {text}")
        return

    if text.lower().startswith("admin "):
        if not is_owner:
            await update.message.reply_text("❌ Only owner can add admins")
            return
        parts = text.split()
        if len(parts) == 2 and parts[1].isdigit():
            new_admin = int(parts[1])
            ADMINS.add(new_admin)
            await update.message.reply_text(f"✅ Added admin: {new_admin}")
        else:
            await update.message.reply_text("❌ Example: admin 123456789")

    elif text.lower().startswith("deladmin "):
        if not is_owner:
            await update.message.reply_text("❌ Only owner can remove admins")
            return
        parts = text.split()
        if len(parts) == 2 and parts[1].isdigit():
            remove_admin = int(parts[1])
            if remove_admin == ADMIN_ID:
                await update.message.reply_text("❌ Can't remove owner")
            elif remove_admin in ADMINS:
                ADMINS.remove(remove_admin)
                await update.message.reply_text(f"🗑 Removed admin: {remove_admin}")
            else:
                await update.message.reply_text("❌ This user is not admin")
        else:
            await update.message.reply_text("❌ Example: deladmin 123456789")

    elif text.lower() == "bot":
        await update.message.reply_text("𝓞𝓝𝓛𝓘𝓝𝓔 ✅")

    elif text.lower() == "id":
        if update.message.reply_to_message:
            replied_user_id = update.message.reply_to_message.from_user.id
            await update.message.reply_text(f"Chat ID: {chat_id}\nUser ID: {replied_user_id}")
        else:
            await update.message.reply_text(f"Chat ID: {chat_id}")

    elif text.lower().startswith("setgp"):
        parts = text.split()
        if len(parts) == 2 and parts[1].lstrip("-").isdigit():
            group_id = int(parts[1])
            await update.message.reply_text(f"✅ set gp Securi: {group_id}")
        else:
            await update.message.reply_text("❌ Example: setgp -1001234567890")

    elif text.lower().startswith("settime"):
        parts = text.split()
        if len(parts) == 2 and parts[1].isdigit():
            timer_seconds = int(parts[1])
            await update.message.reply_text(f"⏳  {timer_seconds} settime ")
        else:
            await update.message.reply_text("❌ Example: settime 2")

    elif text.lower() == "on":
        bot_on = True
        await update.message.reply_text("✅ Bot turned on")

    elif text.lower() == "off":
        bot_on = False
        await update.message.reply_text("⛔ Bot turned off")

    elif text.lower().startswith("addfosh"):
        parts = text.split(maxsplit=1)
        if len(parts) == 2:
            fosh_list.append(parts[1])
            await update.message.reply_text(f"✅ Added: {parts[1]}")
        else:
            await update.message.reply_text("❌ Example: addfosh word")

    elif text.lower().startswith("setuser"):
        parts = text.split()
        if len(parts) == 2 and parts[1].isdigit():
            mention_user_id = int(parts[1])
            await update.message.reply_text(f"✅ Mention user set: {mention_user_id}")
        else:
            await update.message.reply_text("❌ Example: setuser 123456789")

    elif text.lower() == "fosh on":
        if not group_id:
            await update.message.reply_text("Not setgp")
            return
        if not fosh_list:
            await update.message.reply_text("❌ No fosht")
            return
        fosh_mode = True
        await update.message.reply_text("🌪Fosh Turned On")
        asyncio.create_task(spam_fosh(context))

    elif text.lower() == "fosh off":
        fosh_mode = False
        await update.message.reply_text("💤Fosh Turned Off")


# -------- اسپم --------
async def spam_fosh(context):
    global fosh_mode, mention_user_id
    while fosh_mode:
        for word in fosh_list:
            if not fosh_mode:
                break
            try:
                if mention_user_id:
                    mention_text = f"{word}\n\n\n\n\n[𒐦](tg://user?id={mention_user_id})"
                    await context.bot.send_message(chat_id=group_id, text=mention_text, parse_mode="Markdown")
                else:
                    await context.bot.send_message(chat_id=group_id, text=word)
            except Exception as e:
                print("Error:", e)
            await asyncio.sleep(timer_seconds)


# -------- اجرای همه ربات‌ها با Webhook --------
async def start_all_bots():
    apps = []
    for idx, token in enumerate(TOKENS, start=1):
        app = ApplicationBuilder().token(token).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        await app.initialize()
        await app.start()
        await app.bot.set_webhook(f"{WEBHOOK_URL}/{idx}")

        apps.append(app)
        print(f"✅ Bot {idx} started with webhook {WEBHOOK_URL}/{idx}")

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(start_all_bots())
