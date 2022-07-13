__version__ = (0, 0, 8)


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
# 🌐 https://www.gnu.org/licenses/gpl-3.0.html

# meta developer: @apodiktum_modules

# scope: hikka_only
# scope: hikka_min 1.1.28

import logging
import asyncio
import requests

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumTestModuleMod(loader.Module):
    """
    This is a skeleton module.
    """

    strings = {
        "name": "Apo-LibTester",
        "developer": "@anon97945",
        "skeleton_msg": "Base Skeleton String msg.",
        "skeleton2_msg": "Base Skeleton2 String msg.",
    }

    strings_en = {
        "skeleton_msg": "This is a skeleton message.",
        "skeleton2_msg": "This is a skeleton 2 message.",
    }

    strings_de = {
        "skeleton_msg": "Dies ist ein Skeleton Nachricht.",
        "skeleton2_msg": "Dies ist ein Skeleton 2 Nachricht.",
    }

    strings_ru = {
        "skeleton_msg": "Это скелетное сообщение.",
        "skeleton2_msg": "Это скелетное сообщение 2."
    }

    all_strings = {
        "strings": strings,
        "strings_en": strings_en,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    def __init__(self):
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        if not await self.apodiktum_lib_loader(retries=60, delay=1):
            logger.error("ApodiktumLibrary is not loaded.")

    def __getattribute__(self, name):
        if name == "apo_lib":
            if apo_lib := self.lookup("Apo-Library"):
                return apo_lib
            logger.error("Apo-Library is not loaded. Inititiating installation.")
            return asyncio.ensure_future(self.apodiktum_lib_loader(retries=60, delay=1))
        return object.__getattribute__(self, name)

    async def apodiktum_lib_loader(self, retries: int, delay: int):
        apodiktum_lib_name = "Apo-Library"
        apodiktum_lib_link = "https://raw.githubusercontent.com/anon97945/hikka-mods/lib_test/apodiktum_library.py"
        link_valid = requests.head(apodiktum_lib_link).status_code < 400
        load_msg = None
        while True:
            if not retries:
                logger.error("Retries exhausted, gave up trying to resolve %s.", apodiktum_lib_name)
                return False
            if self.lookup(apodiktum_lib_name):
                logger.error("Successfully found %s.", apodiktum_lib_name)
                if load_msg:
                    await load_msg.delete()
                for key in list(self._db["Loader"]["loaded_modules"]):
                    if key == "ApodiktumLibMod":
                        del self._db["Loader"]["loaded_modules"][key]
                        break
                return True

            logger.error("Did not found %s. Trying to download.", apodiktum_lib_name)
            if link_valid:
                load_msg = await self._client.send_message("me", f"{self.get_prefix()}dlmod {apodiktum_lib_link}")
                await self.allmodules.commands["dlmod"](load_msg)
            else:
                async for msgs in self._client.iter_messages(entity=-1001757846320):
                    if "#ApoLibModuleInstaller" in msgs.text:
                        msg = await self._client.send_message("me", message=msgs)
                        break
                if not msg:
                    return False
                await self.allmodules.commands["loadmod"](await msg.edit(f"{self.get_prefix()}loadmod"))
                await msg.delete()
            await asyncio.sleep(delay)
            retries -= 1

    async def skeletoncmd(self, message):
        """
        This is a skeleton command.
        """
        await utils.answer(message, self.apo_lib.get_str("skeleton_msg", self.all_strings, message))
        return

    async def skeleton2cmd(self, message):
        """
        This is a skeleton command.
        """
        await utils.answer(message, self.apo_lib.get_str("skeleton2_msg", self.all_strings, message))
        return

    async def capotestcmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def loggermsgcmd(self, message: Message):
        """
        This will log the message.
        """
        await self.apo_lib._logger("some error message", name=__name__, log_channel=True, error=True, debug_mode=False, debug_msg=False)

    async def refreshlibcmd(self, message: Message):
        logger.error(self.apo_lib)
        self.apo_lib = self.lookup("Apo-Library")
        await utils.answer(message, "Refreshed ApodiktumLibrary.")
