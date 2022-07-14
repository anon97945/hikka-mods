__version__ = (0, 0, 4)


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
# scope: hikka_min 1.2.10

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


@loader.tds
class ApodiktumLibMod(ApodiktumLibraryFunctions, loader.Module):
    """
    This is a Library module required for Apodiktum Modules and also 3rd-party modules.
    >>Do not unload this!<< 
    """

    strings = {
        "name": "Apo-Library",
        "developer": "@anon97945",
        "incorrect_language": "🚫 <b>Incorrect language specified.</b>",
        "lang_saved": "{} <b>forced language saved!</b>",
        "forced_lang": "<b>Forced language {}!</b>",
    }

    strings_de = {
        "_cls_doc": ("Dies ist ein Bibliotheksmodul, das für Apodiktum-Module und auch Module von Drittanbietern benötigt wird."
                     ">>Nicht entfernen!<<"),
        "_cmd_doc_capolib": "Dadurch wird die Konfiguration für das Modul geöffnet.",
    }

    strings_ru = {
        "_cls_doc": ("Это библиотечный модуль, необходимый для модулей Apodiktum, а также для модулей сторонних производителей."
                     ">>Не удаляйте!<<"),
        "_cmd_doc_capolib": "Это откроет конфиг для модуля.",
    }

    def __init__(self):
        self.ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._name = self.strings("name")
        self._classname = self.__class__.__name__
        self._lib_db = self._db[self._classname]
        self._chats_db = self._lib_db.setdefault("chats", {})

    async def capolibcmd(self, message: Message):
        """
        This will open the config for the module.
        """
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {self._name}")
        )

    async def fclcmd(self, message: Message):
        """
        force language of modules in this chat.
        """
        args = utils.get_args_raw(message)
        chat_id = utils.get_chat_id(message)
        chatid_str = str(chat_id)
        chatid_db = self._chats_db.setdefault(chatid_str, {})

        if not args:
            if len(args) not in [0, 2]:
                await utils.answer(message, self.strings("incorrect_language"))
                return
            await utils.answer(
                message,
                self.strings("forced_lang").format(
                    utils.get_lang_flag(chatid_db.get("forced_lang").lower() if chatid_db.get("forced_lang").lower() != "en" else "gb")
                ),
            )
            return

        chatid_db.update({"forced_lang": args.lower()})
        self._db.set(self._classname, "chats", self._chats_db)

        await utils.answer(
            message,
            self.strings("lang_saved").format(
                utils.get_lang_flag(args.lower() if args.lower() != "en" else "gb")
            ),
        )
