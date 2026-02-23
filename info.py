import asyncio
import subprocess
import sys
import importlib
import os

# ==========================================
# 🔧 PYTHON 3.14 EVENT LOOP FIX (MOVED TO TOP)
# ==========================================
# এটি সবার আগে থাকতে হবে, নাহলে Pyrogram ইম্পোর্ট হবে না
try:
    asyncio.get_running_loop()
except RuntimeError:
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    except Exception as e:
        print(f"⚠️ Loop Warning: {e}")

# ==========================================
# 📦 AUTO INSTALL REQUIREMENTS
# ==========================================
def install_package(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        importlib.import_module(import_name)
    except ImportError:
        print(f"📦 Installing missing package: {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"✅ {package_name} installed successfully!")
            # ইনস্টল হওয়ার পর আবার ইম্পোর্ট করে দেখা হচ্ছে যেন ক্যাশ আপডেট হয়
            importlib.invalidate_caches()
            importlib.import_module(import_name)
        except Exception as e:
            print(f"❌ Failed to install {package_name}. Error: {e}")

# লিস্ট: যেগুলো অটো ইনস্টল হবে
requirements = [
    ("pyrogram", "pyrogram"),
    ("tgcrypto", "tgcrypto"),
    ("qrcode", "qrcode"),
    ("Pillow", "PIL")
]

print("🔄 Checking requirements...")
for pkg, imp in requirements:
    install_package(pkg, imp)
print("✅ All requirements checked!\n")


# ===== IMPORTS =====
from pyrogram import Client, filters, enums
import random
import asyncio as aio
import qrcode
import io
import string

# ===== CONFIG =====
# ⚠️ আপনার নিজের API ID এবং HASH এখানে বসাবেন
API_ID = 37316186
API_HASH = "3faf6772d742a5459b169bf965df2174"
BOT_TOKEN = "8321993018:AAGuKxCKKf6-irR36QtiKJ8IzQTxq4dgKYc" 

BOT_NAME = "MrDevilEx"

# ===== APP =====
app = Client("utility_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ===== UTIL =====
async def typing(msg, sec=1):
    try:
        await msg.reply_chat_action(enums.ChatAction.TYPING)
    except Exception:
        pass
    await aio.sleep(sec)

# ===== START =====
@app.on_message(filters.private & filters.command("start"))
async def start(client, message):
    await typing(message)
    await message.reply_text(
        f"👋 Hello {message.from_user.first_name}\n"
        f"I am {BOT_NAME} 🤖\n\n"
        f"Use /help to see commands"
    )

# ===== HELP =====
@app.on_message(filters.private & filters.command("help"))
async def help_cmd(client, message):
    await typing(message)
    await message.reply_text(
        "📌 **Utility Commands**\n\n"
        "📱 **/qr <link/text>** - QR কোড জেনারেটর\n"
        "🔐 **/pass <length>** - পাসওয়ার্ড জেনারেটর\n"
        "🧮 **/calc <math>** - অংক সমাধান\n\n"
        "👤 **/uid** - আপনার আইডি\n"
        "🌐 **/me** - আপনার ইনফো\n"
        "🏓 **/ping** - চেক স্ট্যাটাস\n"
    )

# ==========================================
# 🔥 NEW FEATURE: QR CODE GENERATOR
# ==========================================
@app.on_message(filters.private & filters.command("qr"))
async def generate_qr(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ দয়া করে কোনো টেক্সট বা লিংক দিন।\nউদাহরণ: `/qr facebook.com`")
    
    input_text = message.text.split(None, 1)[1]
    await typing(message)
    msg = await message.reply_text("🔄 জেনারেট হচ্ছে...")

    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(input_text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        bio = io.BytesIO()
        bio.name = "qrcode.png"
        img.save(bio, "PNG")
        bio.seek(0)

        await message.reply_photo(photo=bio, caption=f"✅ QR Code for:\n`{input_text}`")
        await msg.delete()
        
    except Exception as e:
        await msg.edit_text(f"❌ এরর হয়েছে: {e}")

# ==========================================
# 🔥 NEW FEATURE: PASSWORD GENERATOR
# ==========================================
@app.on_message(filters.private & filters.command("pass"))
async def gen_pass(client, message):
    try:
        length = int(message.command[1]) if len(message.command) > 1 else 10
        if length > 100:
            return await message.reply_text("❌ সর্বোচ্চ ১০০ ক্যারেক্টার পর্যন্ত সম্ভব।")

        chars = string.ascii_letters + string.digits + "@#$%&*"
        password = "".join(random.choice(chars) for _ in range(length))
        
        await message.reply_text(f"🔐 আপনার পাসওয়ার্ড (`{length}`):\n\n`{password}`\n\n(কপি করতে ক্লিক করুন)")
    except ValueError:
        await message.reply_text("❌ দয়া করে সঠিক সংখ্যা দিন।")

# ==========================================
# 🔥 NEW FEATURE: CALCULATOR
# ==========================================
@app.on_message(filters.private & filters.command("calc"))
async def calculate(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ অংক দিন। উদাহরন: `/calc 50*2+10`")
    
    expr = message.text.split(None, 1)[1]
    try:
        allowed = set("0123456789+-*/(). ")
        if not set(expr).issubset(allowed):
            return await message.reply_text("❌ ভুল ইনপুট! শুধু সংখ্যা এবং +, -, *, / ব্যবহার করুন।")
        
        result = eval(expr) 
        await message.reply_text(f"🧮 **Result:** `{result}`")
    except Exception:
        await message.reply_text("❌ সমাধান করা যায়নি।")

# ===== OLD UTILS =====
@app.on_message(filters.private & filters.command(["uid", "id"]))
async def uid(client, message):
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    await typing(message)
    caption = (f"👤 Name: {user.first_name}\n🆔 ID: `{user.id}`\n🔗 Username: @{user.username}" if user.username else "No username")
    try:
        async for p in client.get_chat_photos(user.id, limit=1):
            await message.reply_photo(p.file_id, caption=caption)
            return
        await message.reply_text(caption)
    except Exception:
        await message.reply_text(caption)

@app.on_message(filters.private & filters.command("me"))
async def me(client, message):
    u = message.from_user
    await typing(message)
    await message.reply_text(f"👤 Name: {u.first_name}\n🆔 ID: `{u.id}`\n🔗 Username: @{u.username}" if u.username else "No username")

@app.on_message(filters.private & filters.command("ping"))
async def ping(client, message):
    await typing(message, 0.5)
    await message.reply_text("🏓 Pong ✅")

# ===== DETECTOR =====
@app.on_message(filters.private & filters.text)
async def detect(client, message):
    text = message.text.strip()
    if text.startswith("/"): return

    if text.lower() in ["hi", "hello", "hey"]:
        return await message.reply_text(random.choice(["👋 Hello", "Hey 😎", "Hi 🙂"]))

    if text.startswith("@"):
        try:
            chat = await client.get_chat(text)
            uname = f"@{chat.username}" if chat.username else "No username"
            title = chat.title or chat.first_name or "Unknown"
            await message.reply_text(f"👤 Title: {title}\n🆔 ID: `{chat.id}`\n🔗 Username: {uname}")
        except Exception:
            await message.reply_text("❌ Username not found")
        return

    if "t.me/" in text:
        try:
            username = text.split("t.me/")[1].split("/")[0]
            chat = await client.get_chat(username)
            await message.reply_text(f"📢 Title: {chat.title}\n🆔 Chat ID: `{chat.id}`\n👥 Members: {chat.members_count}")
        except Exception:
            await message.reply_text("❌ Cannot fetch group info.")
        return

# ===== RUN =====
print(f"🤖 {BOT_NAME} is Running...")
app.run()