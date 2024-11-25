import json
import os
import re
import random
import asyncio
import subprocess
import logging
import traceback
from plugins.emojis import EMOJIS
from pyrogram import Client, filters
from pyrogram.types import Message
import logging.config

# Set up logging
logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)  

@Client.on_message(filters.text & filters.incoming & filters.command(["info", "mediainfo"]))
async def media_info(client, m: Message):  
    user = m.from_user.first_name
    msg = await m.reply("**Generating... Please wait 🕵️**", quote=True)

    if not (m.reply_to_message and (m.reply_to_message.video or m.reply_to_message.document)):
        await msg.edit_text("**Please reply to a VIDEO, AUDIO, or DOCUMENT to get media information.**")
        logger.warning(f"{user} sent an unsupported or no media.")
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
            logger.warning(f"{user} sent an unsupported media type: {media_type}")
            await msg.edit_text("**This media type is not supported.**")
            return

        mime = media.mime_type
        file_name = media.file_name
        size = media.file_size
        logger.info(f"{user} requested file - Name: {file_name}, Size: {size} bytes")

        if media_type == 'document' and all(x not in mime for x in ['video', 'audio', 'image']):
            logger.warning(f"{user} sent an unsupported document MIME type: {mime}")
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
        mediainfo = subprocess.check_output(['mediainfo', file_name]).decode("utf-8")
        mediainfo_json = json.loads(
            subprocess.check_output(['mediainfo', file_name, '--Output=JSON']).decode("utf-8")
        )
        readable_size = human_size(size)

        try:
            lines = mediainfo.splitlines()
            if 'image' not in mime:
                duration = float(mediainfo_json['media']['track'][0].get('Duration', 0))
                bitrate_kbps = (size * 8) / (duration * 1000) if duration else 0
                bitrate = human_bitrate(bitrate_kbps)

                for i in range(len(lines)):
                    if 'File size' in lines[i]:
                        lines[i] = re.sub(r": .+", f': {readable_size}', lines[i])
                    elif 'Overall bit rate' in lines[i] and 'Overall bit rate mode' not in lines[i]:
                        lines[i] = re.sub(r": .+", f': {bitrate}', lines[i])
                    elif 'IsTruncated' in lines[i] or 'FileExtension_Invalid' in lines[i]:
                        lines[i] = ''

                lines = remove_empty_lines(lines)

            # Write processed mediainfo to a text file
            with open(f"{file_name}.txt", 'w') as f:
                f.write('\n'.join(lines))

            await msg.edit("**SUCCESSFULLY GENERATED ✓**")
            await m.reply_document(document=f"{file_name}.txt", caption=f'`{file_name}`')
            logger.info(f"Media info for {file_name} sent successfully to {user}.")
        finally:
            os.remove(f"{file_name}.txt")

    except Exception as e:
        logger.error(f"Error processing file: {e}\nTraceback:\n{traceback.format_exc()}")
        await msg.edit_text("**An error occurred while processing this file.**")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

def human_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def human_bitrate(bitrate_kbps):
    if bitrate_kbps < 1000:
        return f"{bitrate_kbps:.2f} Kbps"
    return f"{bitrate_kbps / 1000:.2f} Mbps"

def remove_empty_lines(lines):
    return [line for line in lines if line.strip()]
 
