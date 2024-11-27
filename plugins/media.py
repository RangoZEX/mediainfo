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
import logging.config
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
   
# Set up logging
logger = logging.getLogger(__name__)

 
telegraph = Telegraph(domain="graph.org")
  
# Global variable to hold the Telegraph account
telegraph_account = None

# Initialize the Telegraph account once when the bot starts
async def initialize_telegraph():
    global telegraph_account
    if telegraph_account is None:  # Only initialize if not already done
        try:
            account = await telegraph.create_account(
                short_name="@UploadXPro_Bot", 
                author_name="AMC DEV", 
                author_url="https://t.me/amcdev"
            )
            logger.info(f"𝗧𝗲𝗹𝗲𝗴𝗿𝗮𝗽𝗵 𝗔𝗰𝗰𝗼𝘂𝗻𝘁 𝗶𝗻𝗶𝘁𝗶𝗮𝗹𝗶𝘇𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆: {account}")
            telegraph_account = account  # Save account globally
        except Exception as e:
            logger.error(f"Error creating Telegraph account: {e}")
            telegraph_account = None
    return telegraph_account


async def media_size(size):
    if size < 1_073_741_824:  # Less than 1GB
        return f"{size / 1024 / 1024:.2f} MB"
    else:  # Greater than 1GB
        return f"{size / 1024 / 1024 / 1024:.2f} GB"
        

@Client.on_callback_query(filters.regex(r"^info_media$"))
async def handle_mediainfo_callback(client, callback_query):
  
    user = callback_query.from_user.username or callback_query.from_user.first_name
  
    msg = await callback_query.message.edit_text("**G͏e͏n͏e͏r͏a͏t͏i͏n͏g͏ M͏e͏d͏i͏a͏ I͏n͏f͏o͏r͏m͏a͏t͏i͏o͏n͏...🕵️**") 
    await asyncio.sleep(0.7)
    try:
        media_message = callback_query.message.reply_to_message
        if not media_message:
            await msg.edit_text("**Unable to find the media message to process.**")
            return
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
        logger.info(f"🕵️ {user}, Requesting info of:📁 {file_name}, 💽 Size: {(await media_size(size))}")
 
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
        <p><b><a href="https://t.me/MaxxBotOfficial">🔰 @MaxxBotsOfficial</a></b></p>
        <p>ᴘᴏᴡᴇʀᴇᴅ ʙʏ: <a href="https://t.me/amcdev">𝐀𝐌𝐂 𝐃𝐄𝐕</a> | {datetime.now().strftime('%B %d, %Y')}</p>
        <hr><br>
        <h3>📁 <b>{file_name}</b></h3>
        <p>💽 𝗙𝗜𝗟𝗘 𝗦𝗜𝗭𝗘: {(await media_size(size))} </p>
        """
     
        sections = []
     
         # Custom Level map
        custom_labels = {
            'General': '🗒 𝗚𝗘𝗡𝗘𝗥𝗔𝗟 𝗜𝗡𝗙𝗢:',
            'Video': '🎞 𝗩𝗜𝗗𝗘𝗢 𝗜𝗡𝗙𝗢:',
            'Audio': '🔊 𝗔𝗨𝗗𝗜𝗢 𝗜𝗡𝗙𝗢:',
            'Text': '📜 𝗦𝗨𝗕𝗧𝗜𝗧𝗟𝗘𝗦 𝗜𝗡𝗙𝗢:'
        }
        # Add track information (if any)
        for track in mediainfo_json['media'].get('track', []):
            section_type = track.get('@type', 'Unknown')
            label = custom_labels.get(section_type, 'ℹ️ 𝗜𝗡𝗙𝗢')  # Use custom label or default to ℹ️ INFO
            section_content = f"<h3>{label}</h3><pre>"
            for key, value in track.items():
                if key != '@type':
                    section_content += f"{key:<40}: {value}\n"
            section_content += "</pre><br>"
            sections.append(section_content)
 
        content += "".join(sections)

        # Use the already initialized Telegraph account to create a page
        account = await initialize_telegraph()
        if account is None:
            logger.info("Failed to initialize Telegraph account.")
            await msg.edit_text("**Something went wrong while creating telegraph account**")
            return
            
        # Page Create 
        page = await telegraph.create_page(title="🔰Telegram-@UploadXPro_Bot", html_content=content)
        page_url = page['url']
        
        await msg.edit("**ᴜᴘʟᴏᴀᴅɪɴɢ...ɴᴏᴡ😌**")
        logger.info(f"🕵️ 𝘎𝘦𝘯𝘦𝘳𝘢𝘵𝘦 𝘚𝘶𝘤𝘤𝘦𝘴𝘴𝘧𝘶𝘭𝘭𝘺 𝘧𝘰𝘳- {user}, ᴜᴘʟᴏᴀᴅɪɴɢ...ɴᴏᴡ 😌")
        
        await asyncio.sleep(0.5)
        await msg.edit(
            text=f"🕵️ **[ɪɴꜰᴏ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ɢᴇɴᴇʀᴀᴛᴇᴅ ✓]({page_url})**\n\n**URL**: {page_url}",
            disable_web_page_preview=True
        )
        logger.info(f"🕵️ 𝘔𝘦𝘥𝘪𝘢 𝘪𝘯𝘧𝘰 𝘧𝘰𝘳- {file_name} 𝘴𝘦𝘯𝘵 𝘴𝘶𝘤𝘤𝘦𝘴𝘴𝘧𝘶𝘭𝘭𝘺 𝘵𝘰: {user}.")
 
    except Exception as e:
        logger.error(f"Error processing file: {e}\nTraceback:\n{traceback.format_exc()}")
        await msg.edit_text("**An error occurred while processing this file.**")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)
            
