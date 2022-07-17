__version__ = (0, 0, 4)


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
class ApodiktumLibMod(loader.Module):
    """
    This is a Library module required for Apodiktum Modules and also 3rd-party modules.
    """

    strings = {
        "name": "Apo-Library",
        "_cfg_translation_chats": "Define Chats where the translation is forced.",
    }

    strings_de = {
        "_cfg_translation_chats": "Definiere Chats, wo die Übersetzung erzwungen wird.",
        "_cls_doc": (
            "Dies ist ein Bibliotheksmodul, das für Apodiktum-Module und auch Module von Drittanbietern benötigt wird."
        ),
        "_cmd_doc_capolib": "Dadurch wird die Konfiguration für das Modul geöffnet.",
    }

    strings_ru = {
        "_cfg_translation_chats": "Задать чаты, где применяется перевод.",
        "_cls_doc": (
            "Это библиотечный модуль, необходимый для модулей Apodiktum, а также для модулей сторонних производителей."
        ),
        "_cmd_doc_capolib": "Это откроет конфиг для модуля.",
    }

    def __init__(self):
        def lang_chats(name: str) -> loader.ModuleConfig:
            return loader.ConfigValue(
                name,
                doc=lambda: self.strings("_cfg_translation_chats"),
                validator=loader.validators.Series(
                    loader.validators.TelegramID(),
                ),
            )

        self.config = loader.ModuleConfig(
            lang_chats("en_chats"), lang_chats("de_chats"), lang_chats("ru_chats")
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._name = self.strings("name")

    async def capolibcmd(self, message: Message):
        """
        This will open the config for the module.
        """
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {self._name}")
        )

    ### APO ROUTINES

    def get_str(self, string: str, all_strings: dict, message: Message):
        chat_id = utils.get_chat_id(message)
        avail_langs = [k.split("_")[1] for k in all_strings if k != "strings"]
        chat_langs = [
            lang
            for lang in avail_langs
            if self.config[f"{lang}_chats"]
            and chat_id in self.config[f"{lang}_chats"]
        ]

        if len(chat_langs) != 1 or (
            len(chat_langs) == 1 and not all_strings[chat_langs[0]].get(string)
        ):
            ent = "strings"
            self.log(
                "Force translation misconfiguration: %s has invalid language options: %s, or the option does no",
                chat_id,
                chat_langs,
                important=False,
            )
        else:
            ent = f"strings_{chat_langs[0]}"
        try:
            return all_strings[ent][string]
        except KeyError:
            return f"Translation of {string} for {ent} is missing. This is a module bug"

    def log(self, message: str, *args, important=True):
        if self.config["log_all"] or important:
            logger.info(message, *args)
