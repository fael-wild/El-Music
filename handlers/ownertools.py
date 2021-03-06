import sys
import os
import time
import traceback
import asyncio
import shutil
import psutil

from pyrogram import Client, filters
from pyrogram.types import Message, Dialog, Chat
from pyrogram.errors import UserAlreadyParticipant
from datetime import datetime
from functools import wraps
from os import environ, execle, path, remove

from callsmusic.callsmusic import client as pakaya
from helpers.database import db
from helpers.dbtools import main_broadcast_handler
from helpers.decorators import sudo_users_only
from handlers.song import humanbytes, get_text
from config import BOT_USERNAME, OWNER_ID, SUDO_USERS, GROUP_SUPPORT


# Stats Of Your Bot
@Client.on_message(filters.command("stats"))
@sudo_users_only
async def botstats(_, message: Message):
    total, used, free = shutil.disk_usage(".")
    total = humanbytes(total)
    used = humanbytes(used)
    free = humanbytes(free)
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    total_users = await db.total_users_count()
    await message.reply_text(
        text=f"**📊 Stats @{BOT_USERNAME}** \n\n**🤖 Versi Bot:** `v6.5` \n\n**🙎🏼 Pengguna:** \n » **pengguna didalam pm:** `{total_users}` \n\n**💾 Penggunaan Disk,** \n » **ruangan disk:** `{total}` \n » **digunakan:** `{used}({disk_usage}%)` \n » **kosong:** `{free}` \n\n**🎛 Penggunaan hardware,** \n » **penggunaan CPU:** `{cpu_usage}%` \n » **Penggunaan RAM:** `{ram_usage}%`",
        parse_mode="Markdown",
        quote=True
    )



@Client.on_message(filters.private & filters.command("broadcast") & filters.user(OWNER_ID) & filters.reply)
async def broadcast_handler_open(_, m: Message):
    await main_broadcast_handler(m, db)


# Ban User
@Client.on_message(filters.private & filters.command("block") & filters.user(OWNER_ID))
async def ban(c: Client, m: Message):
    if len(m.command) == 1:
        await m.reply_text(
            f"this command for ban user, read /help for more info !",
            quote=True
        )
        return
    try:
        user_id = int(m.command[1])
        ban_duration = int(m.command[2])
        ban_reason = ' '.join(m.command[3:])
        ban_log_text = f"`Membanned pengguna...` \n\nUser ID: `{user_id}` \nDurasi: `{ban_duration}` \nKarena: `{ban_reason}`"
        try:
            await c.send_message(
                user_id,
                f"Maaf, Kamu dibanned!** \n\nKarena: `{ban_reason}` \nDuration: `{ban_duration}` day(s). \n\n**💬 Kirim pesan ke Owner : tanya di @{GROUP_SUPPORT} jika kamu tidak bersalah."
            )
            ban_log_text += '\n\n✅ notifikasi ini sudah terkirim ke pengguna'
        except:
            traceback.print_exc()
            ban_log_text += f"\n\n❌ **gagal mengirim kan notifikasi ke pengguna** \n\n`{traceback.format_exc()}`"
        await db.ban_user(user_id, ban_duration, ban_reason)
        print(ban_log_text)
        await m.reply_text(
            ban_log_text,
            quote=True
        )
    except:
        traceback.print_exc()
        await m.reply_text(
            f"❌ sedang eror occoured !, traceback is given below\n\n`{traceback.format_exc()}`",
            quote=True
        )


# Unban User
@Client.on_message(filters.private & filters.command("unblock") & filters.user(OWNER_ID))
async def unban(c: Client, m: Message):
    if len(m.command) == 1:
        await m.reply_text(
            f"this command for unban user, read /help for more info !",
            quote=True
        )
        return
    try:
        user_id = int(m.command[1])
        unban_log_text = f"`unbanning user...` \n**user id:**{user_id}"
        try:
            await c.send_message(
                user_id,
                f"🎊 Selamat, Kamu sudah tidak di ban , jangan bandel lagi ya!"
            )
            unban_log_text += '\n\n✅ notifikasi ini dikirim ke pengguna'
        except:
            traceback.print_exc()
            unban_log_text += f"\n\n❌ **gagal mengirim notifikasi ke pengguna**\n\n`{traceback.format_exc()}`"
        await db.remove_ban(user_id)
        print(unban_log_text)
        await m.reply_text(
            unban_log_text,
            quote=True
        )
    except:
        traceback.print_exc()
        await m.reply_text(
            f"❌ an error occoured !, traceback is given below\n\n`{traceback.format_exc()}`",
            quote=True
        )


# Banned User List
@Client.on_message(filters.private & filters.command("blocklist") & filters.user(OWNER_ID))
async def _banned_usrs(_, m: Message):
    all_banned_users = await db.get_all_banned_users()
    banned_usr_count = 0
    text = ''
    async for banned_user in all_banned_users:
        user_id = banned_user['id']
        ban_duration = banned_user['ban_status']['ban_duration']
        banned_on = banned_user['ban_status']['banned_on']
        ban_reason = banned_user['ban_status']['ban_reason']
        banned_usr_count += 1
        text += f"⫸ **user id**: `{user_id}`\n⫸ **ban duration**: `{ban_duration}`\n⫸ **banned date**: `{banned_on}`\n⫸ **ban reason**: `{ban_reason}`\n\n"
    reply_text = f"⫸ **total banned:** `{banned_usr_count}`\n\n{text}"
    if len(reply_text) > 4096:
        with open('banned-user-list.txt', 'w') as f:
            f.write(reply_text)
        await m.reply_document('banned-user-list.txt', True)
        os.remove('banned-user-list.txt')
        return
    await m.reply_text(reply_text, True)
