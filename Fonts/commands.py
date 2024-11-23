import logging
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from Fonts.font_list.italic_fonts import FONT

logging.basicConfig(level=logging.DEBUG)

@Client.on_message(filters.private & filters.incoming & filters.text, group=0)
async def font_style(c, m):
    msg = await m.reply("`Checking..🙆`", quote=True)

    # Create buttons dynamically based on available fonts
    buttons = []
    font_names = list(FONT.__dict__.keys())
    for i in range(0, len(font_names), 3):  # Create rows of 3 buttons
        row = [
            InlineKeyboardButton(name, callback_data=name) 
            for name in font_names[i:i + 3]
        ]
        buttons.append(row)

    await msg.edit(
        text="Choose a font style:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^(.*)$"))
async def apply_font(c: Client, cb: CallbackQuery):
    font_name = cb.data
    try:
        selected_font = getattr(FONT, font_name, None)
        if selected_font:
            converted_text = ''.join(
                selected_font.get(char, char) for char in cb.message.text.split(":")[1].strip()
            )
            await cb.message.edit_text(
                text=f"Converted Text ({font_name}):\n{converted_text}",
                reply_markup=cb.message.reply_markup
            )
    except Exception as e:
        logging.error(f"Error applying font: {e}")
        await cb.answer("An error occurred!", show_alert=True)
        
