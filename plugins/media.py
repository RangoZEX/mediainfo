import json
import os
import re
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.private & filters.command("info") & filters.reply)
async def info_command(client, message: Message):
    await tgInfo(client, message)

async def tgInfo(client, msg: Message):
    print("Processing media info...", flush=True)
    message = msg.reply_to_message

    if not message:
        await msg.reply_text("Please reply to a media message to get its information.")
        return

    mediaType = message.media.value

    if mediaType == 'video':
        media = message.video
    elif mediaType == 'audio':
        media = message.audio
    elif mediaType == 'document':
        media = message.document
    else:
        print("This media type is not supported", flush=True)
        await msg.reply_text("This media type is not supported.")
        return

    mime = media.mime_type
    fileName = media.file_name
    size = media.file_size

    print(fileName, size, flush=True)

    if mediaType == 'document':
        if 'video' not in mime and 'audio' not in mime and 'image' not in mime:
            print("Makes no sense", flush=True)
            await msg.reply_text("This file doesn't seem to be a supported media file.")
            return

    if int(size) <= 50000000:
        await message.download(os.path.join(os.getcwd(), fileName))
    else:
        async for chunk in client.stream_media(message, limit=5):
            with open(fileName, 'ab') as f:
                f.write(chunk)

    mediainfo = subprocess.check_output(['mediainfo', fileName]).decode("utf-8")
    mediainfo_json = json.loads(subprocess.check_output(
        ['mediainfo', fileName, '--Output=JSON']).decode("utf-8"))

    readable_size = humanSize(size)

    try:
        lines = mediainfo.splitlines()

        if 'image' not in mime:
            duration = float(mediainfo_json['media']['track'][0]['Duration'])
            bitrate_kbps = (size * 8) / (duration * 1000)
            bitrate = humanBitrate(bitrate_kbps)

            for i in range(len(lines)):
                if 'File size' in lines[i]:
                    lines[i] = re.sub(r": .+", ': ' + readable_size, lines[i])
                elif 'Overall bit rate' in lines[i] and 'Overall bit rate mode' not in lines[i]:
                    lines[i] = re.sub(r": .+", ': ' + bitrate, lines[i])
                elif 'IsTruncated' in lines[i] or 'FileExtension_Invalid' in lines[i]:
                    lines[i] = ''

            lines = remove_N(lines)

        with open(f'{fileName}.txt', 'w') as f:
            f.write('\n'.join(lines))

        await msg.reply_document(document=f'{fileName}.txt', caption=f'`{fileName}`')

        print("Media info sent", flush=True)

        os.remove(f'{fileName}.txt')

    except Exception as e:
        print(f"Error processing file: {e}", flush=True)
        await msg.reply_text("An error occurred while processing this file.")
    
    finally:
        os.remove(fileName)

def humanSize(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def humanBitrate(bitrate_kbps):
    if bitrate_kbps < 1000:
        return f"{bitrate_kbps:.2f} Kbps"
    return f"{bitrate_kbps / 1000:.2f} Mbps"

def remove_N(lines):
    lines = [line for line in lines if line.strip() != '']
    return lines

