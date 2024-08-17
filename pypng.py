__version__ = (0, 0, 32)


# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#           © Copyright 2024
#
#        developed by @anon97945
#
#     https://t.me/apodiktum_modules
#      https://github.com/anon97945
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/gpl-3.0.html

# meta developer: @apodiktum_modules
# meta banner: https://t.me/apodiktum_dumpster/11
# meta pic: https://t.me/apodiktum_dumpster/13

# scope: hikka_only
# scope: hikka_min 1.3.3
# requires: pygments emoji pillow

import logging
import os
from io import BytesIO

import pygments
from pygments.formatters import ImageFormatter
from pygments.lexers import Python3Lexer
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumPyPNGMod(loader.Module):
    """
    Converts link/file from Py to PNG.
    """

    strings = {
        "name": "Apo-PyPNG",
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

    async def client_ready(self):
        self.apo_lib = await self.import_lib(
            "https://raw.githubusercontent.com/anon97945/hikka-libs/master/apodiktum_library.py",
            suspend_on_error=True,
        )

    async def pypngcmd(self, message: Message):
        """
        url/(reply to url or py file)
        """
        await utils.answer(
            message,
            self.apo_lib.utils.get_str("py2png", self.all_strings, message),
        )
        reply = await message.get_reply_message() if message.is_reply else None
        file = BytesIO()
        pngfile = BytesIO()
        args = utils.get_args_raw(message)
        if not message.is_reply and not args:
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_file", self.all_strings, message),
            )
        if message.is_reply:
            if len(self.apo_lib.utils.get_urls(self.apo_lib.utils.raw_text(reply))) > 0:
                url = self.apo_lib.utils.get_urls(self.apo_lib.utils.raw_text(reply))[0]
            else:
                url = None
            if reply.file:
                await self._client.download_file(reply, file)
                file.name = reply.file.name
            if url:
                file, file.name = await self.apo_lib.utils.get_file_from_url(url)
        if not getattr(file, "name", None):
            if args and len(self.apo_lib.utils.get_urls(args)) > 0:
                file, file.name = await self.apo_lib.utils.get_file_from_url(
                    self.apo_lib.utils.get_urls(args)[0]
                )
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
        await self._client.send_file(
            message.peer_id,
            pngfile,
            force_document=True,
            reply_to=reply,
        )
        await message.delete()
