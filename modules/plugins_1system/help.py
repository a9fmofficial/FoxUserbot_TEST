from pyrogram import Client, filters, __version__
from pyrogram.errors import ChatSendPhotosForbidden
from modules.plugins_1system.settings.main_settings import module_list, version
from prefix import my_prefix

from telegraph import Telegraph
from platform import python_version
import random


def get_text(message):
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
    if message.from_user.is_premium:
        return f"""
<emoji id="5190875290439525089">😊</emoji><b> | FoxUserbot RUNNING</b>
<emoji id="5197288647275071607">🛡</emoji><b> | Version: </b><b>{version}</b><b>
<emoji id="5372878077250519677">📱</emoji><b> | Python: {python_version()}</b>
<emoji id="5190637731503415052">🦊</emoji><b> | Kurigram: {__version__}</b>
<emoji id="5193177581888755275">💻</emoji><b> | Modules: {len(module_list)}</b>

<emoji id="5436113877181941026">❓</emoji><a href="{link}"><b> | List of all commands. </b></a>
<emoji id="5330237710655306682">📱</emoji><a href="https://t.me/foxteam0"><b> | Official FoxTeam Channel.</b></a>
<emoji id="5346181118884331907">📱</emoji><a href="https://github.com/FoxUserbot/FoxUserbot"><b> | Github Repository.</b></a>
<emoji id="5379999674193172777">🔭</emoji><a href="https://github.com/FoxUserbot/FoxUserbot#how-to-install"><b> | Installation Guide.</b></a>

<emoji id="5361756547200351182">😈</emoji> | Thanks for using FoxUserbot.
<emoji id="5359700554945689675">😘</emoji> | If you find a malfunction, write issues in github.
"""
    else:
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
        await message.delete()
        da = await client.send_photo(message.chat.id, "https://raw.githubusercontent.com/FoxUserbot/FoxUserbot/refs/heads/main/logo_banner.png",caption="Loading the help menu. Please, wait...")
        await client.edit_message_caption(message.chat.id, da.id, get_text(message))
    except ChatSendPhotosForbidden:
        await message.delete()
        await client.send_message(message.chat.id, get_text(message))


module_list['Help'] = f'{my_prefix()}help'
