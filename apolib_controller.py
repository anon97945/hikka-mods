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

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumLibControllerMod(loader.Module):
    """
    This is a Library Controller module required for Apodiktum Library Modules and also 3rd-party modules.
    >>Do not unload this!<< 
    """

    strings = {
        "name": "Apo-LibController",
        "developer": "@anon97945",
        "incorrect_language": "🚫 <b>Incorrect language specified.</b>",
        "lang_saved": "{} <b>forced language saved!</b>",
        "forced_lang": "<b>Forced language {}!</b>",
    }

    strings_de = {
        "_cls_doc": ("Dies ist ein Bibliothekssteuerungsmodul, das für Apodiktum Library Module und auch Module von Drittanbietern benötigt wird."
                     ">>Nicht entfernen!<<"),
        "_cmd_doc_capolib": "Dadurch wird die Konfiguration für das Modul geöffnet.",
    }

    strings_ru = {
        "_cmd_doc_capolib": "Это откроет конфиг для модуля.",
    }

    def __init__(self):
        self.ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.apo_lib = await self.import_lib(
            "https://pastebin.com/raw/buyVSRC3",
            suspend_on_error=True,
        )
        self._lib_classname = "ApodiktumLib"
        self._lib_db = self._db[self._lib_classname]
        self._chats_db = self._lib_db.setdefault("chats", {})

    async def capolibcmd(self, message: Message):
        """
        This will open the config for the module.
        """
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {self._lib_classname}")
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
        self._db.set(self._lib_classname, "chats", self._chats_db)

        await utils.answer(
            message,
            self.strings("lang_saved").format(
                utils.get_lang_flag(args.lower() if args.lower() != "en" else "gb")
            ),
        )
