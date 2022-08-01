__version__ = (0, 1, 8)


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
# meta pic: https://i.ibb.co/4jLTywZ/apo-modules.jpg

# scope: hikka_only
# scope: hikka_min 1.2.11

import logging

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumTranslationsMod(loader.Module):
    """
    This module handles the db for supported modules to force languages in chats.

    For Devs:
    If you want to implement it into your modules or want to have more languages, you can ask me at @apodiktum_modules
    """

    strings = {
        "name": "Apo-Translations",
        "developer": "@anon97945",
        "_cfg_translation_chats": "Define Chats where the translation is forced.",
    }

    strings_en = {}

    strings_de = {
        "_cfg_translation_chats": "Definiere Chats, wo die Übersetzung erzwungen wird.",
        "_cls_doc": (
            "Dieses Modul verwaltet die Datenbank für unterstützte Module, um"
            " Sprachen in Chats zu erzwingen.Für Entwickler:Wenn ihr es in eure"
            " Module implementieren wollt oder mehr Sprachen haben wollt, könnt"
            " ihr mich unter @apodiktum_modules fragen."
        ),
        "_cmd_doc_ctranslations": (
            "Dadurch wird die Konfiguration für das Modul geöffnet."
        ),
    }

    strings_ru = {
        "_cfg_translation_chats": "Задать чаты, где применяется перевод.",
        "_cls_doc": (
            "Этот модуль обрабатывает db для поддерживаемых модулей для"
            " принудительного использования языков в чатах.Для"
            " разработчиков:Если вы хотите внедрить его в свои модули или"
            " хотите иметь больше языков, вы можете спросить меня в"
            " @apodiktum_modules"
        ),
        "_cmd_doc_ctranslations": "Это откроет конфиг для модуля.",
    }

    all_strings = {
        "strings": strings,
        "strings_en": strings,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "de_chats",
                doc=lambda: self.strings("_cfg_translation_chats"),
                validator=loader.validators.Series(
                    loader.validators.TelegramID(),
                ),
            ),  # for TranslatorStrings
            loader.ConfigValue(
                "en_chats",
                doc=lambda: self.strings("_cfg_translation_chats"),
                validator=loader.validators.Series(
                    loader.validators.TelegramID(),
                ),
            ),  # for TranslatorStrings
            loader.ConfigValue(
                "ru_chats",
                doc=lambda: self.strings("_cfg_translation_chats"),
                validator=loader.validators.Series(
                    loader.validators.TelegramID(),
                ),
            ),  # for TranslatorStrings
            loader.ConfigValue(
                "auto_migrate",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClass
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.apo_lib = await self.import_lib(
            "https://raw.githubusercontent.com/anon97945/hikka-libs/master/apodiktum_library.py",
            suspend_on_error=True,
        )
        self.apo_lib.apodiktum_module()

    async def ctranslationscmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )
