__version__ = (0, 1, 0)


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
# scope: hikka_min 1.1.28
# requires: alphabet-detector

import logging
import asyncio
import time
import googletrans

from telethon.tl.types import Message
from alphabet_detector import AlphabetDetector


from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumLangReplierMod(loader.Module):
    """
    This module automatically respond to messages with unknown languages.
    """

    strings = {
        "name": "Apo-LangReplier",
        "developer": "@anon97945",
        "_cfg_active": "Whether the module is turned on (or not).",
        "_cfg_allowed_alphabets": "The list of alphabets that the module will allow.",
        "_cfg_blacklist_chats": "The list of chats that the module will watch(or not).",
        "_cfg_check_lang": "Whether the module will check the language of the message(or not).",
        "_cfg_custom_message": "The custom message that will be sent.",
        "_cfg_lang_codes": "The list of language codes that the module will ignore.",
        "_cfg_whitelist": "Whether the chatlist includes(True) or excludes(False) the chat.",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "active",
                "True",
                doc=lambda: self.strings("_cfg_turned_on"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "check_language",
                False,
                doc=lambda: self.strings("_cfg_check_lang"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "allowed_alphabets",
                ["latin"],
                lambda: self.strings("_cfg_allowed_alphabets"),
                validator=loader.validators.Series(
                    loader.validators.Choice(["arabic", "cjk", "cyrillic", "greek", "hangul", "hebrew", "hiragana", "katakana", "latin", "thai"])
                ),
            ),
            loader.ConfigValue(
                "chatlist",
                doc=lambda: self.strings("_cfg_blacklist_chats"),
                validator=loader.validators.Series(
                    loader.validators.TelegramID()
                ),
            ),
            loader.ConfigValue(
                "custom_message",
                "<b>[🤖 Automatic]</b> <u>I don't understand {}.</u>\n<b>Sorry.</b> 😉",
                doc=lambda: self.strings("_cfg_custom_message"),
                validator=loader.validators.Union(
                    loader.validators.String(),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "lang_codes",
                ["en"],
                doc=lambda: self.strings("_cfg_lang_codes"),
                validator=loader.validators.Series(
                    loader.validators.String(length=2)
                ),
            ),
            loader.ConfigValue(
                "whitelist",
                True,
                doc=lambda: self.strings("_cfg_whitelist"),
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._fw_protect = {}
        self._fw_protect_limit = 3
        self._ad = AlphabetDetector()
        self._tr = googletrans.Translator()

    def _is_alphabet(self, message):
        text = message.raw_text
        denied_alphabet = ""
        text.encode("utf-8")
        detected_alphabet = self._ad.detect_alphabet(text)
        alphabet_list = [each_string.lower() for each_string in list(detected_alphabet)]
        for found_alphabet in alphabet_list:
            if found_alphabet not in self.config["allowed_alphabets"]:
                denied_alphabet += f", {found_alphabet}" if denied_alphabet else found_alphabet
        allowed_alphabet = not denied_alphabet
        return allowed_alphabet, denied_alphabet

    async def _check_lang(self, message):
        text = message.raw_text
        lang_code = (await utils.run_sync(self._tr.detect, text)).lang
        full_lang = googletrans.LANGUAGES[lang_code]
        return (True, None) if lang_code in self.config["lang_codes"] else (False, full_lang)

    async def calphabetcmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def watcher(self, message):
        respond = False
        full_lang = ""
        if (
            not isinstance(message, Message)
            or not self.config["active"]
            or not message.mentioned
            or message.is_private
            or message.sender_id == self._tg_id
        ):
            return
        user_id = message.sender_id
        chat_id = utils.get_chat_id(message)
        if (
            (self.config["whitelist"] and chat_id not in self.config["chatlist"])
            or (not self.config["whitelist"] and chat_id in self.config["chatlist"])
        ):
            return
        allowed_alphabet, alphabet = self._is_alphabet(message)
        if not allowed_alphabet:
            respond = True
        if self.config["check_language"] and len(message.raw_text.split()) >= 4 and alphabet:
            allowed_lang, full_lang = await self._check_lang(message)
            if not allowed_lang:
                respond = True
        if not respond:
            return
        if (
            user_id in self._fw_protect
            and len(list(filter(lambda x: x > time.time(), self._fw_protect[user_id])))
            >= self._fw_protect_limit
        ):
            return
        if user_id not in self._fw_protect:
            self._fw_protect[user_id] = []
        self._fw_protect[user_id] += [time.time() + 5 * 60]
        if self.config["check_language"] and full_lang:
            msg = await utils.answer(message, self.config["custom_message"].format(full_lang))
        else:
            msg = await utils.answer(message, self.config["custom_message"].format(alphabet))
        await asyncio.sleep(15)
        await msg.delete()
        return
