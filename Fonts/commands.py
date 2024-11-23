import logging
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from Fonts.font_list.italic_fonts import FONT

logging.basicConfig(level=logging.DEBUG)

# Manually map button labels to font names
FONT_BUTTONS = {
    "Old Italic": "OLD_ITALIC",
    "Script Italic": "SCRIPT_ITALIC",
    "Bold Italic": "SCRIPT_BOLD_ITALIC",
    "Serif Bold Italic": "SERIF_BOLD_ITALIC",
    "Sans Serif Italic": "SANS_SERIF_ITALIC",
    "Italic": "ITALIC",
    "Math Italic": "MATH_ALPHA_NUM",
    "Double-Struck Italic": "MATH_DOUBLE_STRUCK_ITALIC",
}

@Client.on_message(filters.private & filters.incoming & filters.text, group=0)
async def font_style(c, m):
    msg = await m.reply("`Checking..🙆`", quote=True)

    # Store the original text for later use in conversion
    original_text = m.text

    # Create buttons dynamically based on the manual button labels
    buttons = []
    button_labels = list(FONT_BUTTONS.keys())
    for i in range(0, len(button_labels), 3):  # Create rows of 3 buttons
        row = [
            InlineKeyboardButton(label, callback_data=f"{FONT_BUTTONS[label]}|{original_text}") 
            for label in button_labels[i:i + 3]
        ]
        buttons.append(row)

    await msg.edit(
        text="Choose a font style:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^(.*)\|(.*)$"))
async def apply_font(c: Client, cb: CallbackQuery):
    try:
        data = cb.data.split("|")
        font_name = data[0]
        original_text = data[1]

        # Fetch the selected font
        selected_font = getattr(FONT, font_name, None)

        if selected_font:
            # Convert the text using the selected font
            converted_text = ''.join(
                selected_font.get(char, char) for char in original_text
            )
            await cb.message.edit_text(
                text=f"Converted Text ({font_name}):\n{converted_text}",
                reply_markup=cb.message.reply_markup  # Keep the buttons intact
            )
        else:
            await cb.answer("Invalid font selection!", show_alert=True)
    except Exception as e:
        logging.error(f"Error applying font: {e}")
        await cb.answer("An error occurred!", show_alert=True)
