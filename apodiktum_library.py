__version__ = (0, 0, 32)


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

import aiohttp
import telethon
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


class ControllerLoader():

    def __init__(
        self,
        modules: loader.Module,
        client: "TelegramClient",  # type: ignore
        db: "Database",  # type: ignore
        classname: str,  # type: ignore
    ):
        logger.debug("class ControllerLoader is being initiated!")
        self._modules = modules
        self._client = client
        self._db = db
        self._classname = classname

    async def ensure_controller(self):
        first_loop = True
        while True:
            if first_loop:
                if not await self._wait_load(delay=5, retries=5) and not self._controller_refresh():
                    await self._init_controller()
                first_loop = False
            elif not self._controller_refresh():
                await self._init_controller()
            await asyncio.sleep(5)

    async def _init_controller(self):
        logger.info("ApoLibController not found, attempting to load...")
        controller_loaded = await self._load_github()
        if controller_loaded:
            return controller_loaded
        self._controller_found = False
        return None

    def _controller_refresh(self):
        if lib_controller := self._modules.lookup("Apo-LibController"):
            self._controller_found = True
        else:
            self._controller_found = False
            logger.info("ApoLibController not found!")
        return lib_controller

    async def _load_github(self):
        link = (
            "https://raw.githubusercontent.com/anon97945/hikka-mods/lib_test/apolib_controller.py"  # Swap this out to the actual libcontroller link!
        )
        async with aiohttp.ClientSession() as session:
            async with session.head(link) as response:
                if response.status >= 300:
                    return None
        link_message = await self._client.send_message(
            "me", f"{self._modules.get_prefix()}dlmod {link}"
        )
        await self._modules.allmodules.commands["dlmod"](link_message)
        lib_controller = await self._wait_load(delay=5, retries=5)
        await link_message.delete()
        return lib_controller

    async def _wait_load(self, delay=5, retries=15):
        while retries:
            if lib_controller := self._modules.lookup("Apo-LibController"):
                logger.info("ApoLibController found!")
                return lib_controller
            if self._modules.lookup("Loader")._fully_loaded:
                retries -= 1
            logger.info("ApoLibController not found, retrying in %s seconds..."
                        "\n Hikka fully loaded: %s", delay, self._modules.lookup("Loader")._fully_loaded)
            await asyncio.sleep(delay)


class ApodiktumLibraryFunctions:
    client: telethon.TelegramClient

    def __init__(self):
        logger.debug("class ApodiktumLibraryFunctions is being loaded!")

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


class ApodiktumLib(loader.Library, ApodiktumLibraryFunctions):
    developer = "@apodiktum_modules"
    version = __version__

    def __init__(self):
        loader.Library.__init__(self)
        ApodiktumLibraryFunctions.__init__(self)

    async def init(self):
        logger.info("Apodiktum Library v%s.%s.%s loading...!", *__version__)
        self._classname = self.__class__.__name__
        self._lib_db = self._db.setdefault(self._classname, {})
        self._chats_db = self._lib_db.setdefault("chats", {})
        self._controllerloader = ControllerLoader(self, self.client, self.db, self.__class__.__name__)
        # await self._controllerloader.init(self.client, self.db, self.__class__.__name__)
        self._acl_task = asyncio.ensure_future(self._controllerloader.ensure_controller())
        logger.info("Apodiktum Library v%s.%s.%s successfully loaded!", *__version__)

    async def on_lib_update():
        self._acl_task.cancel()
