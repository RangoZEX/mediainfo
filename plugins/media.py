import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.private & filters.command("info"))
async def media_info(client, message: Message):
    if message.reply_to_message and message.reply_to_message.document:
        file = message.reply_to_message.document
        file_path = await message.reply_to_message.download()
        try:
            media_info = subprocess.check_output(["mediainfo", file_path])
            media_info = media_info.decode("utf-8")
            
            info_file_path = f"{file.file_name}_info.txt"
            with open(info_file_path, "w") as f:
                f.write(media_info)
            
            await message.reply_document(info_file_path)
        except Exception as e:
            await message.reply("Failed to extract media information.")
          
