import logging
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from Fonts.font_list.italic_fonts import FONT

logging.basicConfig(level=logging.DEBUG)

# Dictionary to store original texts
user_messages = {}

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
async def font_style(c: Client, m):
    msg = await m.reply("`Checking..🙆`", quote=True)

    # Store the original text mapped to the message ID
    user_messages[m.id] = m.text

    # Create buttons dynamically based on the manual button labels
    buttons = []
    button_labels = list(FONT_BUTTONS.keys())
    for i in range(0, len(button_labels), 3):  # Create rows of 3 buttons
        row = [
            InlineKeyboardButton(label, callback_data=f"{FONT_BUTTONS[label]}|{m.id}")
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
        msg_id = int(data[1])

        # Retrieve the original text from the dictionary
        original_text = user_messages.get(msg_id, None)
        if not original_text:
            await cb.answer("Original text not found!", show_alert=True)
            return

        # Fetch the selected font
        selected_font = getattr(FONT, font_name, None)

        if selected_font:
            # Ensure conversion works for all characters
            converted_text = ''.join(
                selected_font.get(char.lower(), char) for char in original_text
            )

            # Handle Telegram's message length limit (4096 characters)
            if len(converted_text) > 4096:
                await cb.message.edit_text("The converted text is too long to display!")
            else:
                await cb.message.edit_text(
                    text=converted_text,
                    reply_markup=cb.message.reply_markup  # Keep the buttons intact
                )
        else:
            await cb.answer("Invalid font selection!", show_alert=True)
    except Exception as e:
        logging.error(f"Error applying font: {e}")
        await cb.answer("An error occurred!", show_alert=True)
        
