from pyrogram import Client, filters, __version__
from pyrogram.errors import ChatSendPhotosForbidden
from modules.plugins_1system.settings.main_settings import module_list, version
from prefix import my_prefix

from telegraph import Telegraph
from platform import python_version
import random

def get_text():
    lists = []
    for k, v in module_list.items():
        lists.append(f'➣ Module [{k}] - Command: {v}<br>')
    a = " "
    for i in lists:
        a = a.lstrip() + f'{i}'
    helpes = f"""
{len(module_list)} available modules.<br>
<br>
{a}
"""
    telegraph = Telegraph()
    telegraph.create_account(short_name='FoxServices')
    link = f"https://telegra.ph/{telegraph.create_page(f'FoxUserbot Help {random.randint(10000, 99999)}', html_content=f'{helpes}')['path']}"
    return f"""
<b>🦊 | FoxUserbot RUNNING</b>
<b>🔒 | Version: {version}</b>
<b>🐍 | Python: {python_version()}</b>
<b>🥧 | Kurigram: {__version__}</b>
<b>💼 | Modules: {len(module_list)}</b>

<b><a href={link}>❓ | List of all commands. </a></b>
<b><a href="https://t.me/foxteam0">💻 | Official FoxTeam Channel.</a></b>
<b><a href="https://github.com/FoxUserbot/FoxUserbot">🐈‍⬛ | Github Repository.</a></b>
<b><a href="https://github.com/FoxUserbot/FoxUserbot#how-to-install">🤔 | Installation Guide.</a></b>

❤️ | Thanks for using FoxUserbot.
❤️ | If you find a malfunction, write issues in github."""

@Client.on_message(filters.command('help', prefixes=my_prefix()) & filters.me)
async def helps(client, message):
    try:
        da = await client.send_photo(message.chat.id, "https://raw.githubusercontent.com/FoxUserbot/FoxUserbot/refs/heads/main/logo_banner.png",caption="Loading the help menu. Please, wait...")
        await client.edit_message_caption(message.chat.id, da.id, get_text())
    except ChatSendPhotosForbidden:
        da = await client.send_message(message.chat.id, "Loading the help menu. Please, wait...")
        await client.edit_message_caption(message.chat.id, da.id, get_text())


module_list['Help'] = f'{my_prefix()}help'
