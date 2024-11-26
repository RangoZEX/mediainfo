from datetime import datetime
import random
import json
import asyncio
import subprocess
import logging
from telegraph import Telegraph
from plugins.emojis import EMOJIS
from pyrogram import Client, filters
from pyrogram.types import Message
import traceback
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Telegraph and create an account if it doesn't exist
telegraph = Telegraph(domain="graph.org")
try:
    telegraph.create_account(short_name="UploadXPro_Bot", author_name="AMC DEV", author_url="https://t.me/amcdev")
except Exception as e:
    logger.info(f"Telegraph account already exists or failed to create: {e}")

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

        # Start building the HTML content with improved design
        content = f"""
        <html>
        <head>
        <style>
        body {{ font-family: Arial, sans-serif; color: #333; }}
        h2 {{ color: #ff6347; }}
        ul {{ margin-top: 5px; }}
        li {{ margin-bottom: 8px; }}
        .section {{ margin-bottom: 20px; }}
        </style>
        </head>
        <body>
        <h2>AMC DEVELOPERS</h2>
        <p><b>@UploadXPro_Bot</b></p>
        <p>{datetime.now().strftime('%B %d, %Y')} by: <a href="https://t.me/amcdev">AMC DEV</a></p>
        <hr><br>

        <div class="section">
        <h3>📁 <b>{file_name}</b></h3>
        <p>File Size: {size / 1024 / 1024:.2f} MB</p>
        </div>
        """

        # Append sections dynamically
        sections = []

        # General section
        general_section = "<div class='section'><h3>🗒 General Information</h3><ul>"
        for key, value in mediainfo_json['media'].items():
            general_section += f"<li><b>{key}:</b> {value}</li>"
        general_section += "</ul></div>"
        sections.append(general_section)

        # Video, Audio, and other sections
        for track in mediainfo_json['media']['track']:
            section_type = track.get('@type', 'Unknown')
            emoji = section_dict.get(section_type, 'ℹ️')
            section_content = f"<div class='section'><h3>{emoji} {section_type} Information</h3><ul>"
            for key, value in track.items():
                if key != '@type':
                    section_content += f"<li><b>{key}:</b> {value}</li>"
            section_content += "</ul></div>"
            sections.append(section_content)

        content += "".join(sections)

        # Closing HTML tags
        content += "</body></html>"

        # Create the page on Telegraph
        page = telegraph.create_page(title=f"UploadXPro_Bot", html_content=content)
        page_url = page['url']

        await msg.edit(f"**MediaInfo Successfully Generated ✓**\n\n[Click here to view media information]({page_url})")
        logger.info(f"🕵️ Media info for {file_name} sent successfully to: {user}.")

    except Exception as e:
        logger.error(f"Error processing file: {e}\nTraceback:\n{traceback.format_exc()}")
        await msg.edit_text("**An error occurred while processing this file.**")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)
            
