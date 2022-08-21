__version__ = (0, 1, 12)


# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#           © Copyright 2022
#
#        developed by @anon97945
#
#     https://t.me/apodiktum_modules
#      https://github.com/anon97945
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/gpl-3.0.html

# meta developer: @apodiktum_modules
# meta banner: https://t.me/file_dumbster/11
# meta pic: https://t.me/file_dumbster/13

# scope: hikka_only
# scope: hikka_min 1.3.3

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
        "forced_lang": "<b>Forced language {}!</b>",
        "incorrect_language": "🚫 <b>Incorrect language specified.</b>",
        "lang_removed": "<b>Forced chat language removed!</b>",
        "lang_saved": "{} <b>forced chat language saved!</b>",
        "no_lang": "No forced language in this chat.",
        "version_str": "📦 <b>Last installed Apodiktum Library was <code>{}</code>.</b>",
    }

    strings_en = {}

    strings_de = {
        "_cls_doc": (
            "Dies ist ein Bibliothekssteuerungsmodul, das für Apodiktum Library"
            " Module und auch Module von Drittanbietern benötigt wird.>>Nicht"
            " entfernen!<<"
        ),
        "_cmd_doc_capolib": "Dadurch wird die Konfiguration für das Modul geöffnet.",
    }

    strings_ru = {
        "_cmd_doc_capolib": "Это откроет конфиг для модуля.",
    }

    all_strings = {
        "strings": strings,
        "strings_en": strings_en,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    def __init__(self):
        self.ratelimit = []

    async def client_ready(self):
        self.apo_lib = await self.import_lib(
            "https://raw.githubusercontent.com/anon97945/hikka-libs/master/apodiktum_library.py",
            suspend_on_error=True,
        )
        self.apo_lib.apodiktum_module()
        self._lib_classname = self.apo_lib.__class__.__name__
        self._lib_db = self._db[self._lib_classname]
        self._chats_db = self._lib_db.setdefault("chats", {})

    async def capolibcmd(self, message: Message):
        """
        This will open the config for the module.
        """
        await self.allmodules.commands["config"](
            await utils.answer(
                message, f"{self.get_prefix()}config {self._lib_classname}"
            )
        )

    async def vapolibcmd(self, message: Message):
        """
        shows the current version of the apodiktum_library.
        """
        lib_version = self._lib_db.get("version", "unknown")
        if lib_version != "unknown":
            version_str = f"v{lib_version[0]}.{lib_version[1]}.{lib_version[2]}"
        else:
            version_str = lib_version
        await utils.answer(
            message,
            self.apo_lib.utils.get_str("version_str", self.all_strings, message).format(
                version_str
            ),
        )

    async def fclcmd(self, message: Message):
        """
        <langcode> | force language of supported modules in this chat.
        """
        args = utils.get_args_raw(message)
        chat_id = utils.get_chat_id(message)
        chatid_str = str(chat_id)
        chatid_db = self._chats_db.setdefault(chatid_str, {})

        if not args:
            if len(args) not in [0, 2]:
                await utils.answer(
                    message,
                    self.apo_lib.utils.get_str("incorrect_language"),
                    self.all_strings,
                    message,
                )
                return
            if "forced_lang" in chatid_db:
                await utils.answer(
                    message,
                    self.apo_lib.utils.get_str(
                        "forced_lang", self.all_strings, message
                    ).format(
                        utils.get_lang_flag(
                            chatid_db.get("forced_lang").lower()
                            if chatid_db.get("forced_lang").lower() != "en"
                            else "gb"
                        )
                    ),
                )
            else:
                await utils.answer(
                    message,
                    self.apo_lib.utils.get_str("no_lang", self.all_strings, message),
                )
            return

        chatid_db.update({"forced_lang": args.lower()})
        self._db.set(self._lib_classname, "chats", self._chats_db)

        await utils.answer(
            message,
            self.apo_lib.utils.get_str("lang_saved", self.all_strings, message).format(
                utils.get_lang_flag(args.lower() if args.lower() != "en" else "gb")
            ),
        )

    async def remfclcmd(self, message: Message):
        """
        remove force language in this chat.
        """
        chat_id = utils.get_chat_id(message)
        chatid_str = str(chat_id)
        chatid_db = self._chats_db.setdefault(chatid_str, {})

        if chatid_db.get("forced_lang"):
            chatid_db.pop("forced_lang")
        self._db.set(self._lib_classname, "chats", self._chats_db)

        await utils.answer(
            message,
            self.apo_lib.utils.get_str("lang_removed", self.all_strings, message),
        )

    @loader.watcher(only_messages=True)
    async def watcher(self, message: Message):
        await self.apo_lib.watcher_q.msg_reciever(message)
