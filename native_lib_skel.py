__version__ = (0, 0, 2)


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

# scope: hikka_only
# scope: hikka_min 1.2.10

import logging

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class SkeletonMod(loader.Module):
    """
    This is a skeleton module.
    """

    strings = {
        "name": "SkeletonMod",
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
        "strings_en": strings,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self.apo_lib = await self.import_lib(
            "https://pastebin.com/raw/buyVSRC3",
            suspend_on_error=True,
        )

    # Port these commands to the actual lib!

    async def hellocmd(self, message: Message):
        await utils.answer(
            message, self.apo_lib.get_str("greet", self.all_strings, message)
        )

    async def watcher(self, message: Message):
        if isinstance(message, Message) and message.message == "ApoSkelWatcher":
            await utils.answer(message, "Skeleton")
