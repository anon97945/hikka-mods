__version__ = (0, 1, 26)


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
# requires: alphabet-detector googletrans==4.0.0-rc1

import asyncio
import logging
import time

import googletrans
from alphabet_detector import AlphabetDetector
from telethon.tl.types import Message

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
        "_cfg_check_lang": (
            "Whether the module will check the language of the message(or not)."
        ),
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_custom_message": "The custom message that will be sent.",
        "_cfg_lang_codes": "The list of language codes that the module will ignore.",
        "_cfg_vodka_mode": (
            "Whether the module will replace `cyrillic` in reply message with `vodka`."
        ),
        "_cfg_whitelist": (
            "Whether the chatlist includes(True) or excludes(False) the chat."
        ),
        "_cfg_auto_translate": (
            "Whether the module will auto translate the message(or not)."
        ),
    }

    strings_en = {}

    strings_de = {}

    strings_ru = {}

    all_strings = {
        "strings": strings,
        "strings_en": strings,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "active",
                True,
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
                "auto_translate",
                "en",
                doc=lambda: self.strings("_cfg_auto_translate"),
                validator=loader.validators.Union(
                    loader.validators.String(length=2),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "allowed_alphabets",
                ["latin"],
                lambda: self.strings("_cfg_allowed_alphabets"),
                validator=loader.validators.Series(
                    loader.validators.Choice(
                        [
                            "arabic",
                            "cjk",
                            "cyrillic",
                            "greek",
                            "hangul",
                            "hebrew",
                            "hiragana",
                            "katakana",
                            "latin",
                            "thai",
                        ]
                    )
                ),
            ),
            loader.ConfigValue(
                "chatlist",
                doc=lambda: self.strings("_cfg_blacklist_chats"),
                validator=loader.validators.Series(loader.validators.TelegramID()),
            ),
            loader.ConfigValue(
                "custom_message",
                "<b>[🤖 Automatic]</b> <u>I don't understand"
                " {}.</u><br><b>Sorry.</b> 😉{}",
                doc=lambda: self.strings("_cfg_custom_message"),
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "custom_transl_msg",
                "<br><br>Translation"
                " <code>{}</code>-><code>{}</code><br><code>{}</code>",
                doc=lambda: self.strings("_cfg_custom_message"),
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "lang_codes",
                ["en"],
                doc=lambda: self.strings("_cfg_lang_codes"),
                validator=loader.validators.Series(loader.validators.String(length=2)),
            ),
            loader.ConfigValue(
                "vodka_mode",
                False,
                doc=lambda: self.strings("_cfg_vodka_mode"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "whitelist",
                True,
                doc=lambda: self.strings("_cfg_whitelist"),
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
        self._fw_protect = {}
        self._fw_protect_limit = 3
        self._ad = AlphabetDetector()
        self._tr = googletrans.Translator()

    def _is_alphabet(self, message):
        text = self.apo_lib.utils.raw_text(message)
        denied_alphabet = ""
        text.encode("utf-8")
        detected_alphabet = self._ad.detect_alphabet(text)
        alphabet_list = [each_string.lower() for each_string in list(detected_alphabet)]
        for found_alphabet in alphabet_list:
            if (
                found_alphabet not in self.config["allowed_alphabets"]
                and found_alphabet != "mathematical"
            ):
                denied_alphabet += (
                    f", {found_alphabet}" if denied_alphabet else found_alphabet
                )
        allowed_alphabet = not denied_alphabet
        return allowed_alphabet, denied_alphabet, detected_alphabet

    async def _check_lang(self, message):
        text = self.apo_lib.utils.raw_text(message)
        lang_code = (await utils.run_sync(self._tr.detect, text)).lang
        if lang_code in googletrans.LANGUAGES:
            full_lang = googletrans.LANGUAGES[lang_code]
        else:
            full_lang = lang_code
        return (
            (True, None, None)
            if lang_code in self.config["lang_codes"]
            else (False, full_lang, lang_code)
        )

    async def clangrepliercmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    @loader.watcher("only_messages", "in")
    async def watcher(self, message: Message):
        if (
            not self.config["active"]
            or message.is_private
            or not message.mentioned
            or (
                self.config["whitelist"]
                and utils.get_chat_id(message) not in self.config["chatlist"]
            )
            or (
                not self.config["whitelist"]
                and utils.get_chat_id(message) in self.config["chatlist"]
            )
        ):
            return

        full_lang = ""
        delay = 15
        user_id = message.sender_id
        allowed_alphabet, alphabet, detected_alphabet = self._is_alphabet(message)
        respond = not allowed_alphabet
        if self.apo_lib.utils.is_emoji(self.apo_lib.utils.raw_text(message)):
            return
        if (
            self.config["check_language"]
            and len(self.apo_lib.utils.raw_text(message).split()) >= 4
            and len(self.apo_lib.utils.raw_text(message)) >= 12
            and detected_alphabet
            and not respond
        ) or (self.config["auto_translate"]):
            allowed_lang, full_lang, lang_code = await self._check_lang(message)
            if not allowed_lang:
                respond = True
        if not respond or (
            user_id in self._fw_protect
            and len(list(filter(lambda x: x > time.time(), self._fw_protect[user_id])))
            >= self._fw_protect_limit
        ):
            return

        if user_id not in self._fw_protect:
            self._fw_protect[user_id] = []

        self._fw_protect[user_id] += [time.time() + 5 * 60]
        if self.config["auto_translate"]:
            text = self.apo_lib.utils.raw_text(message).lower()
            to_lang = self.config["auto_translate"]
            translated = (
                await utils.run_sync(
                    self._tr.translate, text, dest=to_lang, src=lang_code
                )
            ).text
            delay = 30

        if self.config["check_language"] and full_lang:
            if self.config["auto_translate"]:
                msg = await message.reply(
                    self.config["custom_message"]
                    .format(
                        full_lang,
                        self.config["custom_transl_msg"].format(
                            lang_code, to_lang, translated
                        ),
                    )
                    .replace("<br>", "\n")
                )
            else:
                msg = await message.reply(
                    self.config["custom_message"]
                    .format(full_lang)
                    .replace("<br>", "\n")
                )
        else:
            if self.config["vodka_mode"] and "cyrillic" in alphabet:
                alphabet = alphabet.replace("cyrillic", "vodka")
            if self.config["auto_translate"]:
                msg = await message.reply(
                    self.config["custom_message"]
                    .format(
                        alphabet,
                        self.config["custom_transl_msg"].format(
                            lang_code, to_lang, translated
                        ),
                    )
                    .replace("<br>", "\n")
                )
            else:
                msg = await message.reply(
                    self.config["custom_message"].format(alphabet).replace("<br>", "\n")
                )

        await asyncio.sleep(delay)
        await msg.delete()
