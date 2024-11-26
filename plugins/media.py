# ©RangoZex - Owner 
import traceback
import os
import asyncio
import random
import json
import subprocess
import logging
from datetime import datetime
from telegraph.aio import Telegraph
from plugins.emojis import EMOJIS
from pyrogram import Client, filters
from pyrogram.types import Message


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

telegraph = Telegraph(domain="graph.org")

async def initialize_telegraph():
    return await telegraph.create_account(
        short_name="UploadXPro_Bot", 
        author_name="AMC DEV", 
        author_url="https://t.me/amcdev"
    )

async def main():
    account = await initialize_telegraph()

section_dict = {'General': '🗒', 'Video': '🎞', 'Audio': '🔊', 'Text': '🔠', 'Menu': '🗃'}

@Client.on_message(filters.text & filters.incoming & filters.command(["info", "mediainfo"]))
async def media_info(client, m: Message):
    user = m.from_user.first_name
    msg = await m.reply("**Generating... Please wait 🕵️**", quote=True)

    if not (m.reply_to_message and (m.reply_to_message.video or m.reply_to_message.document)):
        await msg.edit_text("**Please reply to a VIDEO, AUDIO, or DOCUMENT to get media information.**")
        logger.warning(f"🕵️ {user}, sent an unsupported or no media.")
        return

    try:
        random_emoji = random.choice(EMOJIS.EMOJI_LIST)
        await client.send_reaction(
            chat_id=m.chat.id,
            message_id=m.id,
            emoji=random_emoji,
            big=True
        )
    except Exception as e:
        logger.error(f"Error sending reaction: {e}\nTraceback:\n{traceback.format_exc()}")

    await asyncio.sleep(0.5)
    media_message = m.reply_to_message
    media_type = media_message.media.value

    try:
        if media_type == 'video':
            media = media_message.video
        elif media_type == 'audio':
            media = media_message.audio
        elif media_type == 'document':
            media = media_message.document
        else:
            logger.warning(f"🕵️ {user}, sent an unsupported media type: {media_type}")
            await msg.edit_text("**This media type is not supported.**")
            return

        mime = media.mime_type
        file_name = media.file_name
        size = media.file_size
        logger.info(f"🕵️ {user}, Requests info of:📁 {file_name}, 💽 Size: {size} bytes")

        if media_type == 'document' and all(x not in mime for x in ['video', 'audio', 'image']):
            logger.warning(f"🤡 {user}, sent an unsupported document MIME type: {mime}")
            await msg.edit_text("**This document type is not supported.**")
            return

        if size <= 50_000_000:
            await media_message.download(file_name)
            logger.info(f"Downloaded file: {file_name}")
        else:
            logger.info(f"Streaming file: {file_name}")
            async for chunk in client.stream_media(media_message, limit=5):
                with open(file_name, 'ab') as f:
                    f.write(chunk)

        mediainfo_json = json.loads(
            subprocess.check_output(['mediainfo', file_name, '--Output=JSON']).decode("utf-8")
        )

        content = f"""
        <h2>AMC DEVELOPERS</h2>
        <p><b>@UploadXPro_Bot</b></p>
        <p>{datetime.now().strftime('%B %d, %Y')} by: <a href="https://t.me/amcdev">AMC DEV</a></p>
        <hr><br>

        <div class="section">
        <h3>📁 <b>{file_name}</b></h3>
        <p>File Size: {size / 1024 / 1024:.2f} MB</p>
        </div>
        """

        sections = []

        general_section = "<div class='section'><h3>🗒 General Information</h3><pre>"
        for key, value in mediainfo_json['media'].items():
            general_section += f"{key:<40}: {value}\n"
        general_section += "</pre></div><br>"
        sections.append(general_section)

        for track in mediainfo_json['media']['track']:
            section_type = track.get('@type', 'Unknown')
            emoji = section_dict.get(section_type, 'ℹ️')
            section_content = f"<div class='section'><h3>{emoji} {section_type} Information</h3><pre>"
            for key, value in track.items():
                if key != '@type':
                    section_content += f"{key:<40}: {value}\n"
            section_content += "</pre></div><br>"
            sections.append(section_content)

        content += "".join(sections)

        page = await telegraph.create_page(title="UploadXPro_Bot", html_content=content)
        page_url = page['url']

        await msg.edit(f"**MediaInfo Successfully Generated ✓**\n\n[Click here to view media information]({page_url})")
        logger.info(f"🕵️ Media info for {file_name} sent successfully to: {user}.")

    except Exception as e:
        logger.error(f"Error processing file: {e}\nTraceback:\n{traceback.format_exc()}")
        await msg.edit_text("**An error occurred while processing this file.**")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)
            
