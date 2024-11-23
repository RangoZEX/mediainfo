import logging
from Fonts.font_list.italic_fonts import FONT
from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

logging.basicConfig(level=logging.DEBUG)

# Initialize the list of font names and dictionaries
FONT_STYLES = {
    "OLD_ITALIC": FONT.OLD_ITALIC,
    "SCRIPT_ITALIC": FONT.SCRIPT_ITALIC,
    "SCRIPT_BOLD_ITALIC": FONT.SCRIPT_BOLD_ITALIC,
    "SERIF_BOLD_ITALIC": FONT.SERIF_BOLD_ITALIC,
    "SANS_SERIF_ITALIC": FONT.SANS_SERIF_ITALIC,
    "ITALIC": FONT.ITALIC,
    "MATH_ALPHA_NUM": FONT.MATH_ALPHA_NUM,
    "MATH_DOUBLE_STRUCK_ITALIC": FONT.MATH_DOUBLE_STRUCK_ITALIC,
}

@Client.on_message(filters.private & filters.text, group=0)
async def font_style(c, m):
    msg = await m.reply("`Checking..🙆`", quote=True)
    try:
        # Dynamically create the list of buttons for all available fonts
        buttons = [
            [InlineKeyboardButton(font_name, callback_data=font_name) for font_name in FONT_STYLES.keys()]
        ]
        await msg.edit(
            text="Choose a font style:",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )
    except KeyError as e:
        logging.error(f"Error in font style generation: {e}")
        await msg.edit(text="An error occurred while processing your request.")

# A single callback handler to process all font style requests
@Client.on_callback_query(filters.regex("^(?!cancel).*$"))
async def handle_font_style(c, callback_query: CallbackQuery):
    font_name = callback_query.data
    if font_name not in FONT_STYLES:
        return  # If the font is not valid, do nothing
    
    # Retrieve the text from the message the user is replying to
    user_text = callback_query.message.reply_to_message.text if callback_query.message.reply_to_message else "Sample Text"
    
    # Convert the text to the selected font
    font_dict = FONT_STYLES[font_name]  # Get the corresponding font dictionary
    converted_text = ''.join([font_dict.get(char.lower(), char) for char in user_text])  # Convert each char
    
    # Send the converted text as a reply
    await callback_query.message.edit(text=f"**{font_name}:**\n{converted_text}")
    
