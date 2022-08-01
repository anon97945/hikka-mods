__version__ = (0, 0, 24)


# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#           © Copyright 2022
#
#        developed by @anon97945
#
#     https://t.me/apodiktum_modules
#      https://github.com/anon97945
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/gpl-3.0.html

# meta developer: @apodiktum_modules
# meta banner: https://t.me/file_dumbster/11
# meta pic: https://i.ibb.co/4jLTywZ/apo-modules.jpg

# scope: hikka_only
# scope: hikka_min 1.2.11
# requires: pygments requests emoji

import logging
import os
from io import BytesIO

import pygments
from pygments.formatters import ImageFormatter
from pygments.lexers import Python3Lexer
from requests import get
from telethon.tl.types import Message

from .. import loader, utils

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
class ApodiktumPyPNGMod(loader.Module):
    """
    Converts link/file from Py to PNG.
    """

    strings = {
        "name": "Apo PyPNG",
        "developer": "@anon97945",
        "no_file": "<b>Reply to file.py or url</b>",
        "no_url": "<b>No url in reply found.</b>",
        "py2png": "<b>Converting Py to PNG</b>",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
    }

    strings_en = {}

    strings_de = {}

    strings_ru = {}

    all_strings = {
        "strings": strings,
        "strings_en": strings,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "auto_migrate",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClass
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.apo_lib = await self.import_lib(
            "https://raw.githubusercontent.com/anon97945/hikka-libs/master/apodiktum_library.py",
            suspend_on_error=True,
        )
        self.apo_lib.apodiktum_module()

    async def pypngcmd(self, message: Message):
        """
        reply to url or py file
        """
        await utils.answer(
            message,
            self.apo_lib.utils.get_str("py2png", self.all_strings, message),
        )
        reply = await message.get_reply_message()
        file = BytesIO()
        pngfile = BytesIO()
        if not reply:
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_file", self.all_strings, message),
            )
        if reply.file:
            await message.client.download_file(reply, file)
            file.name = reply.file.name
        elif res := await _filefromurl(reply):
            file, file.name = res
        else:
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_url", self.all_strings, message),
            )
        file.seek(0)
        byte_str = file.read()
        text = byte_str.decode("utf-8")
        pygments.highlight(
            text,
            Python3Lexer(),
            ImageFormatter(font_name="DejaVu Sans Mono", line_numbers=True),
            pngfile,
        )
        pngfile.name = f"{os.path.splitext(file.name)[0]}.png"
        pngfile.seek(0)
        await message.client.send_file(
            message.to_id, pngfile, force_document=True, reply_to=reply
        )
        await message.delete()
