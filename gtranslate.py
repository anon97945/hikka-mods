__version__ = (0, 0, 72)


# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#           © Copyright 2024
#
#        developed by @anon97945
#
#     https://t.me/apodiktum_modules
#      https://github.com/anon97945
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/gpl-3.0.html

# meta developer: @apodiktum_modules
# meta banner: https://t.me/apodiktum_dumpster/11
# meta pic: https://t.me/apodiktum_dumpster/13

# scope: hikka_only
# scope: hikka_min 1.3.3
# requires: googletrans==4.0.0-rc1

import logging

import googletrans
from telethon.tl.types import Message

from .. import loader, utils

if googletrans.__version__ != "4.0.0-rc.1":
    raise ImportError(  # This will force Hikka to attempt dependency re-installation
        f"The googletrans version is {googletrans.__version__}, not"
        ' "4.0.0-rc.1".It means the module cannot run properly. To fix this,'
        " reinstall googletrans==4.0.0-rc1..terminal pip install"
        " googletrans==4.0.0-rc1"
    )


logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumGTranslateMod(loader.Module):
    """
    Google Translator
    """

    strings = {
        "name": "Apo-GoogleTranslator",
        "developer": "@anon97945",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_lang_msg": "Language to translate to by default.",
        "_cfg_vodkatr_msg": "If `RU` should be displayed as `Vodka`.",
        "invalid_text": "Invalid text to translate",
        "split_error": (
            "Python split() error, if there is -> in the text, it must split!"
        ),
        "translated": (
            "<b>[ <code>{frlang}</code> -> </b><b><code>{to}</code>"
            " ]</b>\n<code>{output}</code>"
        ),
        "translating": "Translating...",
    }

    strings_en = {}

    strings_de = {
        "_cfg_lang_msg": "Sprache, in die standardmäßig übersetzt werden soll.",
        "_cfg_vodkatr_msg": "Ob `RU` als `Vodka` angezeigt werden soll.",
        "_cmd_doc_cgtranslate": (
            "Dadurch wird die Konfiguration für das Modul geöffnet."
        ),
        "invalid_text": "Ungültiger Text zum Übersetzen.",
        "split_error": (
            "Python split() error, wenn -> im Text steht, muss es gesplittet werden!"
        ),
        "translated": (
            "<b>[ <code>{frlang}</code> -> </b><b><code>{to}</code>"
            " ]</b>\n<code>{output}</code>"
        ),
        "translating": "Übersetze...",
    }

    strings_ru = {
        "_cfg_lang_msg": "Язык на который переводится по умолчанию.",
        "_cfg_vodkatr_msg": "Если `RU`, то должно отображаться как `Vodka`.",
        "_cmd_doc_cgtranslate": "Это откроет конфиг для модуля.",
        "invalid_text": "Неправильный текст для перевода",
        "split_error": (
            "Ошибка в функции Python – split(). Если в тексте есть ->, то это"
            " должно быть разделено."
        ),
        "translated": (
            "<b>[ <code>{frlang}</code> -> </b><b><code>{to}</code>"
            " ]</b>\n<code>{output}</code>"
        ),
        "translating": "Переводим...",
    }

    all_strings = {
        "strings": strings,
        "strings_en": strings,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    changes = {
        "migration1": {
            "name": {
                "old": "Apo GoogleTranslator",
                "new": "Apo-GoogleTranslator",
            },
        },
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "DEFAULT_LANG",
                "en",
                doc=lambda: self.strings("_cfg_lang_msg"),
                validator=loader.validators.String(length=2),
            ),
            loader.ConfigValue(
                "vodka_easteregg",
                False,
                doc=lambda: self.strings("_cfg_vodkatr_msg"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "auto_migrate",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClass
        )

    async def client_ready(self):
        self.apo_lib = await self.import_lib(
            "https://raw.githubusercontent.com/anon97945/hikka-libs/master/apodiktum_library.py",
            suspend_on_error=True,
        )
        self.tr = googletrans.Translator()

    async def cgtranslatecmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def gtranslatecmd(self, message: Message):
        """.gtranslate [from_lang->][->to_lang] <text>"""
        args = utils.get_args(message)

        if len(args) == 0 or "->" not in args[0]:
            text = " ".join(args)
            args = ["", self.config["DEFAULT_LANG"]]
        else:
            text = " ".join(args[1:])
            args = args[0].split("->")

        if not text and message.is_reply:
            text = (await message.get_reply_message()).message
        if len(text) == 0:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("invalid_text", self.all_strings, message),
            )
            return
        if args[0] == "":
            args[0] = (await utils.run_sync(self.tr.detect, text)).lang
        if len(args) == 3:
            del args[1]
        if len(args) == 1:
            logging.error(self.strings("split_error"))
            raise RuntimeError()
        if args[1] == "":
            args[1] = self.config["DEFAULT_LANG"]
        args[0] = args[0].lower()
        await utils.answer(
            message,
            self.apo_lib.utils.get_str("translating", self.all_strings, message),
        )
        translated = (
            await utils.run_sync(self.tr.translate, text, dest=args[1], src=args[0])
        ).text
        ret = self.apo_lib.utils.get_str("translated", self.all_strings, message)
        if self.config["vodka_easteregg"]:
            args = list(map(lambda x: x.replace("ru", "vodka"), args))
        ret = ret.format(
            text=utils.escape_html(text),
            frlang=utils.escape_html(args[0]),
            to=utils.escape_html(args[1]),
            output=utils.escape_html(translated),
        )
        await utils.answer(message, ret)
