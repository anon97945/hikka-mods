__version__ = (0, 0, 47)


# ▄▀█ █▄░█ █▀█ █▄░█ █▀▄ ▄▀█ █▀▄▀█ █░█ █▀
# █▀█ █░▀█ █▄█ █░▀█ █▄▀ █▀█ █░▀░█ █▄█ ▄█
#
#              © Copyright 2022
#
#          https://t.me/apodiktum_modules
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @anon97945

# scope: hikka_only
# requires: googletrans==4.0.0-rc1

import logging
import googletrans

from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import Message
from .. import loader, utils

if googletrans.__version__ != "4.0.0-rc.1":
    raise KeyError(f"The googletrans version is {googletrans.__version__}, not \"4.0.0-rc.1\"."
                   "It means the module cannot run properly. To fix this, reinstall googletrans==4.0.0-rc1.")


logger = logging.getLogger(__name__)


@loader.tds
class gtranslateMod(loader.Module):
    """Google Translator"""
    strings = {
        "name": "Google Translator",
        "dev_channel": "@apodiktum_modules",
        "translated": "<b>[ <code>{frlang}</code> -> </b><b><code>{to}</code> ]</b>\n<code>{output}</code>",
        "invalid_text": "Invalid text to translate",
        "split_error": "Python split() error, if there is -> in the text, it must split!",
        "_cfg_lang_msg": "Language to translate to by default.",
        "_cfg_vodkatr_msg": "If `RU` should be displayed as `Vodka`.",
    }

    strings_de = {
        "translated": "<b>[ <code>{frlang}</code> -> </b><b><code>{to}</code> ]</b>\n<code>{output}</code>",
        "invalid_text": "Ungültiger Text zum Übersetzen.",
        "split_error": "Python split() error, wenn -> im Text steht, muss es gesplittet werden!",
        "_cfg_lang_msg": "Sprache, in die standardmäßig übersetzt werden soll.",
        "_cfg_vodkatr_msg": "Ob `RU` als `Vodka` angezeigt werden soll.",
    }

    strings_ru = {
        "name": "Google Translator",
        "translated": "<b>[ <code>{frlang}</code> -> </b><b><code>{to}</code> ]</b>\n<code>{output}</code>",
        "invalid_text": "Неправильный текст для перевода",
        "split_error": "Ошибка в функции Python – split(). Если в тексте есть ->, то это должно быть разделено.",
        "_cfg_lang_msg": "Язык на который переводится по умолчанию.",
        "_cfg_vodkatr_msg": "Если `RU`, то должно отображаться как `Vodka`.",
        "translated_by": "@MUTANTP7AY3R5",
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
                "False",
                doc=lambda: self.strings("_cfg_vodkatr_msg"),
                validator=loader.validators.Boolean(),
            ),
        )

    async def on_dlmod(self, client: TelegramClient, _):
        await client(JoinChannelRequest(channel=self.strings("dev_channel")))

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._me = await client.get_me()
        self.tr = googletrans.Translator()

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
            await message.edit(self.strings["invalid_text"])
            return
        if args[0] == "":
            args[0] = (await utils.run_sync(self.tr.detect, text)).lang
        if len(args) == 3:
            del args[1]
        if len(args) == 1:
            logging.error(self.strings["split_error"])
            raise RuntimeError()
        if args[1] == "":
            args[1] = self.config["DEFAULT_LANG"]
        args[0] = args[0].lower()
        translated = (await utils.run_sync(self.tr.translate, text, dest=args[1], src=args[0])).text
        ret = self.strings["translated"]
        if self.config["vodka_easteregg"]:
            args = list(map(lambda x: x.replace("ru", "vodka"), args))
        ret = ret.format(text=utils.escape_html(text), frlang=utils.escape_html(args[0]),
                         to=utils.escape_html(args[1]), output=utils.escape_html(translated))
        await utils.answer(message, ret)
