import json
import os
import random
import asyncio
import subprocess
import logging
import traceback
from datetime import datetime
from telegraph import Telegraph
from plugins.emojis import EMOJIS
from pyrogram import Client, filters
from pyrogram.types import Message

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize Telegraph
telegraph = Telegraph()
telegraph.create_account(short_name="UploadXPro_Bot", author_name="AMC DEV", author_url="https://t.me/amcdev")

# Section emoji mapping
section_dict = {'General': '🗒', 'Video': '🎞', 'Audio': '🔊', 'Text': '🔠', 'Subtitle': '💬'}

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
        # Determine media type and fetch media details
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

        # Download or stream the file
        if size <= 50_000_000:  # Direct download for smaller files
            await media_message.download(file_name)
            logger.info(f"Downloaded file: {file_name}")
        else:  # Stream large files
            logger.info(f"Streaming file: {file_name}")
            async for chunk in client.stream_media(media_message, limit=5):
                with open(file_name, 'ab') as f:
                    f.write(chunk)

        # Run mediainfo subprocess
        mediainfo_json = json.loads(
            subprocess.check_output(['mediainfo', file_name, '--Output=JSON']).decode("utf-8")
        )

        # Parse and structure media info
        content = f"""
<b>AMC DEVELOPERS</b><br>

<b>@UploadXPro_Bot</b><br>
{datetime.now().strftime('%B %d, %Y')} by: <a href="https://t.me/amcdev">AMC DEV</a><br><br>

📌 <b>{file_name}</b><br><br>
"""

        for track in mediainfo_json['media']['track']:
            section_type = track.get('@type', 'Unknown')
            emoji = section_dict.get(section_type, 'ℹ️')
            content += f"<b>{emoji} {section_type}:</b><br><ul>"

            for key, value in track.items():
                if key != '@type':
                    content += f"<li><b>{key}:</b> {value}</li>"
            content += "</ul><br>"

        # Create Telegraph page
        page_title = "@UploadXPro_Bot"
        page = telegraph.create_page(title=page_title, html_content=content)
        page_url = page['url']

        await msg.edit(f"**MediaInfo Successfully Generated ✓**\n\n[Click here to view media information]({page_url})")
        logger.info(f"🕵️ Media info for, {file_name} sent successfully to: {user}.")

    except Exception as e:
        logger.error(f"Error processing file: {e}\nTraceback:\n{traceback.format_exc()}")
        await msg.edit_text("**An error occurred while processing this file.**")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)
            
