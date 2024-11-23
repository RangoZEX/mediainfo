import logging
import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
 
logging.basicConfig(level=logging.DEBUG)
 
 
START_TEXT = """**Hey {},**\n
 
**This is Font Style Generate Bot.
- just send me any text **:
"""
 
@Client.on_callback_query(filters.regex("^start$"))                    
@Client.on_message(filters.private & filters.command("start"))
async def start(c, m):
    last_name = f' {m.from_user.last_name}' if m.from_user.last_name else ''
    mention = f"[{m.from_user.first_name}{last_name}](tg://user?id={m.from_user.id})"
 
    if not getattr(m, 'data', None):
        maxx = await m.reply("**__Processing..__** ⏳", quote=True)
    else:
        maxx = m.message
    await maxx.edit(
         text=START_TEXT.format(mention),
         reply_markup=InlineKeyboardMarkup(
             [
                 [
                     InlineKeyboardButton('Close ❌', callback_data='cancel')
                 ]
             ]
         ),
         disable_web_page_preview=True,
    )
 
 
