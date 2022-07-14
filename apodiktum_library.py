__version__ = (0, 0, 5)


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


import logging
import telethon

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


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


class ApodiktumLib(ApodiktumLibraryFunctions, loader.Library):
    developer = "@apodiktum_modules"

    async def init(self):
        self._classname = self.__class__.__name__
        self._lib_db = self._db[self._classname]
        self._chats_db = self._lib_db.setdefault("chats", {})
