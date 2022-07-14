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


import asyncio
import logging
from typing import Callable

import aiohttp
import telethon
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


class ControllerLoader():
    client: telethon.TelegramClient

    async def ensure_controller(self):
        while True:
            if not self._controller_refresh():
                await self._init_controller()
            await asyncio.sleep(5)

    async def _init_controller(self):
        logger.error("ApoLibController not found, attempting to load...")
        load_github = await self._load_github()
        if load_github:
            return load_github
        self._controller_found = False
        return None

    def _controller_refresh(self):
        if maybe_controller :=self.modules.lookup("Apo-LibController"):
            self._controller_found = True
            logger.error("ApoLibController found!")
            return maybe_controller
        else:
            self._controller_found = False
            logger.error("ApoLibController not found!")
            return False

    async def _load_github(self):
        link = (
            "https://raw.githubusercontent.com/anon97945/hikka-mods/lib_test/apolib_controller.py"  # Swap this out to the actual libcontroller link!
        )
        async with aiohttp.ClientSession() as session:
            async with session.head(link) as response:
                if response.status >= 300:
                    return None
        link_message = await self.client.send_message(
            "me", f"{self.get_prefix()}dlmod {link}"
        )
        await self.allmodules.commands["dlmod"](link_message)
        maybe_controller = await self._wait_load()
        await link_message.delete()
        return maybe_controller

    async def _wait_load(self):
        retries = 50
        delay = 5
        while retries:
            if maybe_controller := self.modules.lookup("Apo-LibController"):
                return maybe_controller
            retries -= 1
            logger.error("ApoLibController not found, retrying in %s seconds", delay)
            await asyncio.sleep(delay)


class ApodiktumLibraryFunctions:
    client: telethon.TelegramClient

    def get_str(self, string: str, all_strings: dict, message: Message):
        base_strings = "strings"
        if chat_id := utils.get_chat_id(message):
            chatid_db = self._chats_db.setdefault(str(chat_id), {})
            forced_lang = chatid_db.get("forced_lang")
            languages = {base_strings: all_strings[base_strings]}
            for lang, strings in all_strings.items():
                if len(lang.split("_", 1)) == 2:
                    languages[lang.split('_', 1)[1]] = {**all_strings[base_strings], **all_strings[lang]}
            for lang, strings in languages.items():
                if lang and forced_lang == lang:
                    if string in strings:
                        return strings[string].replace("<br>", "\n")
                    break
        return all_strings[base_strings][string].replace("<br>", "\n")

    def _logger(self, log_string: str, name: str, log_channel: bool = True, error: bool = True, debug_mode: bool = False, debug_msg: bool = False):
        apo_logger = logging.getLogger(name)
        if (not debug_msg and log_channel and not error) or (debug_mode and debug_msg):
            return apo_logger.info(log_string)
        if error:
            return apo_logger.error(log_string)
        return apo_logger.debug(log_string)


class ApodiktumLib(ControllerLoader, ApodiktumLibraryFunctions, loader.Library):
    developer = "@apodiktum_modules"

    async def init(self):
        self._classname = self.__class__.__name__
        self._lib_db = self._db[self._classname]
        self._chats_db = self._lib_db.setdefault("chats", {})
        # return asyncio.ensure_future(self.ensure_controller()) #  Lookup does not work with libs(?)
        logger.info("Apodiktum Library v%s.%s.%s successfully loaded!", *__version__)
