__version__ = (0, 0, 9)


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
# scope: hikka_min 1.1.28

import asyncio
import logging
from typing import Callable

import aiohttp
import telethon
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


class ApoModule:
    client: telethon.TelegramClient

    async def _wait_load(self):
        retries = 5
        delay = 5
        while retries:
            if maybe_apo := self.lookup("Apo-Library"):
                return maybe_apo
            retries -= 1
            logger.error("ApoLib not found, retrying in %s seconds", delay)
            await asyncio.sleep(delay)

    async def _load_github(self):
        link = (
            "https://raw.githubusercontent.com/anon97945/hikka-mods/lib_test/apodiktum_library.py"  # Swap this out to the actual lib link!
        )
        async with aiohttp.ClientSession() as session:
            async with session.head(link) as response:
                if response.status >= 300:
                    return None
        link_message = await self.client.send_message(
            "me", f"{self.get_prefix()}dlmod {link}"
        )
        await self.allmodules.commands["dlmod"](link_message)
        maybe_apo = await self._wait_load()
        await link_message.delete()
        return maybe_apo

    async def _load_telegram(self):
        msg = None
        async for msgs in self.client.iter_messages(entity=-1001757846320):
            if msgs.text and "#ApoLibModuleInstaller" in msgs.text:
                msg = await self.client.send_message("me", message=msgs)
                break
        if not msg:
            logger.error("Could not find ApoLib in telegram.")
            return False
        await self.allmodules.commands["loadmod"](await msg.edit(f"{self.get_prefix()}loadmod"))
        maybe_apo = await self._wait_load()
        await msg.delete()
        return maybe_apo

    async def ensure_apo(self):
        if not self._apo_refresh():
            await self._init_apo()

    async def _init_apo(self):
        maybe_github = await self._load_github()
        if maybe_github:
            return maybe_github
        maybe_telegram = await self._load_telegram()
        if maybe_telegram:
            return maybe_telegram
        self._apo_found = False
        return None

    def _apo_refresh(self):
        if maybe_apo :=self.lookup("Apo-Library"):
            self._apo_found = True
            logger.error("ApoLib found!")
            return maybe_apo
        else:
            self._apo_found = False
            logger.error("ApoLib not found!")
            return None


    def _handle_uninit(self, cmd_func: Callable):
        async def handling(message: Message):
            if not getattr(cmd_func.__self__, "_apo_found", True):
                logger.error("Could not find ApoLib for module %s", __class__.__name__)
                await self.ensure_apo()
                return
            await cmd_func(message)

        handling.__self__ = self
        return handling

    def __getattribute__(self, __name: str):
        if __name == "apo":
            return self._apo_refresh()
        val = super().__getattribute__(__name)
        if __name.endswith("cmd") or __name == "watcher":
            return self._handle_uninit(val)
        return val


@loader.tds
class SkeletonMod(loader.Module, ApoModule):
    """
    This is a skeleton module.
    """

    strings = {
        "name": "SkeletonMod",
        "greet": "BaseString Hello!",
    }

    strings_en = {"greet": "Hello!"}

    strings_ru = {"greet": "Привет!"}

    strings_de = {"greet": "Hallo!"}

    all_strings = {
        "strings": strings,
        "strings_en": strings_en,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        await self.ensure_apo()  # Has to be present whether you use apo in client_ready or not
        if self.apo:
            self.apo._logger("Hello from client_ready!", name=__class__.__name__, log_channel=True, error=True, debug_mode=False, debug_msg=False)

    # Port these commands to the actual lib!

    async def hellocmd(self, message: Message):
        await utils.answer(
            message, self.apo.get_str("greet", self.all_strings, message)
        )

    async def watcher(self, message: Message):
        if isinstance(message, Message) and message.message == "ApoSkelWatcher":
            await utils.answer(message, "Skeleton")
