# scope: hikka_only

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
        retries = 500
        delay = 5
        while retries:
            maybe_apo = self.lookup("Apo-Library")
            if maybe_apo:
                return maybe_apo
            retries -= 1
            await asyncio.sleep(delay)

    async def _load_github(self):
        link = (
            "https://pastebin.com/raw/rifYtTiE"  # Swap this out to the actual lib link!
        )
        async with aiohttp.ClientSession() as session:
            async with session.head(link) as response:
                if response.status >= 300:
                    return None
        link_message = await self.client.send_message(
            "me", self.get_prefix() + "dlmod " + link
        )
        await self.allmodules.commands["dlmod"](link_message)
        return await self._wait_load()

    async def _load_telegram(self):
        return None

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
        maybe_apo = self.lookup("Apo-Library")
        if maybe_apo:
            return maybe_apo

    def _handle_uninit(self, cmd_func: Callable):
        async def handling(message: Message):
            if not getattr(cmd_func.__self__, "_apo_found", True):
                await utils.answer(message, "Could not find ApoLib")
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
class SkeletonMod(ApoModule, loader.Module):
    """
    This is a skeleton module.
    """

    strings = {"name": "Skeleton"}

    strings_en = {"greet": "Hello!"}

    strings_ru = {"greet": "Привет!"}

    strings_de = {"greet": "Hallo!"}

    all_strings = {
        "strings": {**strings, **strings_en},  # Python 3.8 is sad
        "strings_en": strings_en,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        await self.ensure_apo()  # Has to be present whether you use apo in client_ready or not
        if self.apo:
            self.apo.log("Hello from client_ready!")

    # Port these commands to the actual lib!

    async def hellocmd(self, message: Message):
        await utils.answer(
            message, self.apo.get_str("greet", self.all_strings, message)
        )

    async def watcher(self, message: Message):
        if message.message == "Skel":
            await utils.answer(message, "Skeleton")
