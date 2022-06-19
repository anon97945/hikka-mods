__version__ = (0, 0, 9)


# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#              © Copyright 2022
#
#             developed by @anon97945
#
#          https://t.me/apodiktum_modules
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @apodiktum_modules

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
    for url in urll:
        if "://" in url:
            text = get(url).text
            file = BytesIO(bytes(text, "utf-8"))
            file.name = url.split("/")[-1]
            return file, file.name
    return False


@loader.tds
class pypngMod(loader.Module):
    """
    Converts link/file from Py to PNG.
    """
    strings = {
        "name": "PyPNG",
        "developer": "@anon97945",
        "no_file": "<b>Reply to file.py or url</b>",
        "no_url": "<b>No url in reply found.</b>",
        "py2png": "<b>Converting Py to PNG</b>",
    }

    async def client_ready(self, client, db):
        self.client = client

    async def get_media(self, message: Message):
        file = (
            BytesIO((await self.fast_download(message.media)).getvalue())
        )
        file.seek(0)
        return file

    async def pypngcmd(self, message: Message):
        """
        reply to url or py file
        """
        await utils.answer(message, self.strings("py2png"))
        reply = await message.get_reply_message()
        file = BytesIO()
        pngfile = BytesIO()
        if not reply:
            return await utils.answer(message, self.strings("no_file"))
        if reply.file:
            file = await self.get_media(reply)
            file.name = reply.file.name
        elif res := await _filefromurl(reply):
            file, file.name = res
        else:
            return await utils.answer(message, self.strings("no_url"))
        file.seek(0)
        byte_str = file.read()
        text = byte_str.decode("utf-8")
        pygments.highlight(text, Python3Lexer(), ImageFormatter(font_name="DejaVu Sans Mono", line_numbers=True), pngfile)
        pngfile.name = f"{os.path.splitext(file.name)[0]}.png"
        pngfile.seek(0)
        await message.client.send_file(message.to_id, await self.fast_upload(pngfile), force_document=True, reply_to=reply)
        await message.delete()
