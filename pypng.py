__version__ = (0, 0, 2)


# ▄▀█ █▄░█ █▀█ █▄░█ █▀▄ ▄▀█ █▀▄▀█ █░█ █▀
# █▀█ █░▀█ █▄█ █░▀█ █▄▀ █▀█ █░▀░█ █▄█ ▄█
#
#              © Copyright 2022
#
#          https://t.me/apodiktum_modules
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @anon97945

# scope: hikka_only
# scope: hikka_min 1.1.28
# requires: pygments requests

import logging
import pygments
import os


from .. import loader, utils
from telethon.tl.types import Message
from io import BytesIO
from requests import get
from pygments.lexers import Python3Lexer
from pygments.formatters import ImageFormatter


logger = logging.getLogger(__name__)


async def _filefromurl(message):
    urll = message.raw_text.split()
    url_found = False
    for url in urll:
        if "://" in url:
            url_found = True
            break
    if not url_found:
        return False
    text = get(url).text
    file = BytesIO(bytes(text, "utf-8"))
    file.name = url.split("/")[-1]
    file.seek(0)
    return file, file.name


@loader.tds
class py2pngMod(loader.Module):
    """Uploader"""
    strings = {
        "name": "pypng",
        "py2png": "<b>Converting Py to PNG</b>",
        "no_file": "<b>Reply to file.py</b>",
        "no_url": "<b>No url in reply found.</b>",
    }

    async def client_ready(self, client, db):
        self.client = client

    async def pypngcmd(self, message: Message):
        """reply to text code or py file"""
        await utils.answer(message, self.strings("py2png"))
        reply = await message.get_reply_message()
        file = BytesIO()
        if not reply:
            return await utils.answer(message, self.strings("no_file"))
        if media := reply.media:
            await message.client.download_file(media, file)
            file.name = reply.file.name
        elif res := await _filefromurl(reply):
            file, file.name = res
        else:
            return await utils.answer(message, self.strings("no_url"))
        file.seek(0)
        byte_str = file.read()
        text = byte_str.decode("utf-8")
        pygments.highlight(text, Python3Lexer(), ImageFormatter(font_name="DejaVu Sans Mono", line_numbers=True), file.name)
        await message.client.send_file(message.to_id, file.name, force_document=True)
        await message.delete()
