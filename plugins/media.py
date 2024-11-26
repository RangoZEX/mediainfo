import traceback
import os
import asyncio
import random
import json
import subprocess
import logging
from datetime import datetime
from telegraph.aio import Telegraph
from pyrogram import Client, filters
from pyrogram.types import Message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

telegraph = Telegraph(domain="graph.org")

# Initialize the Telegraph account every time the script runs
async def initialize_telegraph():
    try:
        account = await telegraph.create_account(
            short_name="Telegram- @UploadXPro_Bot", 
            author_name="AMC DEV", 
            author_url="https://t.me/amcdev"
        )
        logger.info(f"Telegraph Account initialized successfully: {account}")
        return account
    except Exception as e:
        logger.error(f"Error creating Telegraph account: {e}")
        return None


async def media_size(size):
    if size < 1_073_741_824:  # Less than 1GB
        return f"{size / 1024 / 1024:.2f} MB"
    else:  # Greater than 1GB
        return f"{size / 1024 / 1024 / 1024:.2f} GB"
        
# Function to handle media info command
@Client.on_message(filters.text & filters.incoming & filters.command(["info", "mediainfo"]))
async def media_info(client, m: Message):
    user = m.from_user.first_name
    msg = await m.reply("**Generating... Please wait 🕵️**", quote=True)

    if not (m.reply_to_message and (m.reply_to_message.video or m.reply_to_message.document)):
        await msg.edit_text("**Please reply to a VIDEO, AUDIO, or DOCUMENT to get media information.**")
        logger.warning(f"🕵️ {user}, sent an unsupported or no media.")
        return

    await asyncio.sleep(1)
    media_message = m.reply_to_message

    try:
        # Check media type and fetch media info
        if media_message.video:
            media = media_message.video
            media_type = 'video'
        elif media_message.audio:
            media = media_message.audio
            media_type = 'audio'
        elif media_message.document:
            media = media_message.document
            media_type = 'document'
        else:
            logger.warning(f"🕵️ {user}, sent an unsupported media type.")
            await msg.edit_text("**This media type is not supported.**")
            return

        mime = media.mime_type
        file_name = media.file_name
        size = media.file_size
        logger.info(f"🕵️ {user}, Requesting info of:📁 {file_name}, 💽 Size: {(await media_size(size))} bytes")

        # Handle unsupported document types
        if media_type == 'document' and all(x not in mime for x in ['video', 'audio', 'image']):
            logger.warning(f"🤡 {user}, sent an unsupported document MIME type: {mime}")
            await msg.edit_text("**This document type is not supported.**")
            return

        # Handle download or streaming of the media
        if size <= 50_000_000:
            await media_message.download(file_name)
            logger.info(f"Downloaded file: {file_name}")
        else:
            logger.info(f"Streaming file: {file_name}")
            async for chunk in client.stream_media(media_message, limit=5):
                with open(file_name, 'ab') as f:
                    f.write(chunk)

        # Run MediaInfo command to get detailed information
        mediainfo_json = json.loads(
            subprocess.check_output(['mediainfo', file_name, '--Output=JSON']).decode("utf-8")
        )

        # Prepare content for the Telegraph page
        content = f"""
        <p><b>🔰 @MaxxBotOfficial</b></p>
        <p>{datetime.now().strftime('%B %d, %Y')} by: <a href="https://t.me/amcdev">AMC DEV</a></p>
        <hr><br>
        <h3>📁 <b>{file_name}</b></h3>
        <p>💽 File Size: {(await media_size(size))} </p>
        """

        sections = []

        general_section = "<h3>🗒 General Information</h3><pre>"
        for key, value in mediainfo_json['media'].items():
            general_section += f"{key:<40}: {value}\n"
        general_section += "</pre><br>"
        sections.append(general_section)

        # Add track information (if any)
        for track in mediainfo_json['media'].get('track', []):
            section_type = track.get('@type', 'Unknown')
            emoji = {'General': '🗒', 'Video': '🎞', 'Audio': '🔊', 'Subtitles': '📜', 'Menu': '🗃'}.get(section_type, 'ℹ️')
            section_content = f"<h3>{emoji} {section_type} Information</h3><pre>"
            for key, value in track.items():
                if key != '@type':
                    section_content += f"{key:<40}: {value}\n"
            section_content += "</pre><br>"
            sections.append(section_content)

        content += "".join(sections)

        # Initialize Telegraph account and create the page
        account = await initialize_telegraph()
        if account is None:
            await msg.edit_text("**Failed to initialize Telegraph account.**")
            return

        page = await telegraph.create_page(title="UploadXPro_Bot", html_content=content)
        page_url = page['url']
        await msg.edit("**Generate Successfully. Uploading...now😌**")
        await asyncio.sleep(1)
        await msg.edit(f"**MediaInfo Successfully Generated ✓**\n\n[Click here to view media information]({page_url})")
        logger.info(f"🕵️ Media info for {file_name} sent successfully to: {user}.")

    except Exception as e:
        logger.error(f"Error processing file: {e}\nTraceback:\n{traceback.format_exc()}")
        await msg.edit_text("**An error occurred while processing this file.**")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)
            
