__version__ = (0, 0, 12)


# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#              © Copyright 2022
#
#             developed by @secondtimeusername
#
#          https://t.me/apodiktum_modules
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/gpl-3.0.html

# meta developer: @apodiktum_modules
# meta banner: https://i.ibb.co/N7c0Ks2/cat.jpg
# meta pic: https://i.ibb.co/4jLTywZ/apo-modules.jpg

# scope: hikka_only
# scope: hikka_min 1.2.11
# requires: emoji

import logging

import emoji  # skipcq: PY-W2000
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApoLibTesterMod(loader.Module):
    """
    This is a skeleton module.
    """

    strings = {
        "name": "Apo-LibTester",
        "greet": "BaseString Hello!",
    }

    strings_en = {
        "greet": "Hello!",
    }

    strings_ru = {
        "greet": "Привет!",
    }

    strings_de = {
        "greet": "Hallo!",
    }

    all_strings = {
        "strings": strings,
        "strings_en": strings_en,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self.apo_lib = await self.import_lib(
            "https://raw.githubusercontent.com/anon97945/hikka-mods/master/apodiktum_library.py",
            suspend_on_error=True,
        )
        self.apo_lib.apodiktum_module()

    async def hellocmd(self, message: Message):
        await utils.answer(
            message, self.apo_lib.utils.get_str("greet", self.all_strings, message)
        )

    async def lmsgcmd(self):
        """
        This will log the message.
        """
        self.apo_lib.utils.log(logging.ERROR, __name__, "some error log")

    async def ldebugcmd(self):
        """
        This will log the message.
        """
        self.apo_lib.utils.log(logging.DEBUG, __name__, "some debug error")

    async def ldebugmsgcmd(self):
        """
        This will log the message.
        """
        self.apo_lib.utils.log(
            logging.DEBUG, __name__, "some debug message", debug_msg=True
        )
