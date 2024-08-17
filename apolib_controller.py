__version__ = (0, 1, 20)


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

import asyncio
import contextlib
import logging
import re

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
        "q_pending": "\n<code>   - Pending:</code> <code>{}</code>",
        "q_total_count": "\n<code>   - Total count:</code> <code>{}</code>",
        "q_watcher_str": (
            "<b><u><i>Queue"
            " Watcher:</i></u></b>\n<b>Queue:</b>\n<code>{}</code>\n\n<b>Tasks:</b>\n<code>{}</code>"
        ),
        "queues": "<b><u><i>Queues:</i></u></b>",
        "t_cancelled": "\n<code>   - Cancelled:</code> <code>{}</code>",
        "t_done": "\n<code>   - Done:</code> <code>{}</code>",
        "t_id": "\n<code>   - ID:</code> <code>{}</code>",
        "t_name": "\n<code>   - Name:</code> <code>{}</code>",
        "tasks": "<b><u><i>Tasks:</i></u></b>",
        "version_str": "📦 <b>Current Apodiktum Library <code>{}</code>.</b>",
    }

    strings_de = {
        "_cls_doc": (
            "Dies ist ein Bibliothekssteuerungsmodul, das für Apodiktum Library"
            " Module und auch Module von Drittanbietern benötigt wird.\n>>Nicht"
            " entfernen!<<"
        ),
        "_cmd_doc_capolib": "Dadurch wird die Konfiguration für das Modul geöffnet.",
        "_cmd_doc_vapolib": (
            "Zeigt die aktuelle Version des Apodiktum_Library Moduls an."
        ),
        "_cmd_doc_qapolib": (
            "Zeigt die aktuellen Queues und Tasks der Apodiktum Library an."
        ),
        "forced_lang": "<b>Für diesen Chat ist die Sprache {}!</b>",
        "incorrect_language": "🚫 <b>Falsche Sprache angegeben.</b>",
        "lang_removed": "<b>Für diesen Chat wurde die Sprache entfernt!</b>",
        "lang_saved": "{} <b>Sprache für diesen Chat gespeichert!</b>",
        "no_lang": "Keine Sprache für diesen Chat gesetzt.",
        "q_pending": "\n<code>   - Ausstehend:</code> <code>{}</code>",
        "q_total_count": "\n<code>   - Total count:</code> <code>{}</code>",
        "q_watcher_str": (
            "<b><u><i>Queue"
            " Watcher:</i></u></b>\n<b>Queue:</b>\n<code>{}</code>\n\n<b>Tasks:</b>\n<code>{}</code>"
        ),
        "queues": "<b><u><i>Queues:</i></u></b>",
        "t_cancelled": "\n<code>   - Abgebrochen:</code> <code>{}</code>",
        "t_done": "\n<code>   - Abgeschlossen:</code> <code>{}</code>",
        "t_id": "\n<code>   - ID:</code> <code>{}</code>",
        "t_name": "\n<code>   - Name:</code> <code>{}</code>",
        "tasks": "<b><u><i>Tasks:</i></u></b>",
        "version_str": "📦 <b>Aktuelle Apodiktum_Library <code>{}</code>.</b>",
    }

    strings_ru = {
        "_cmd_doc_capolib": "Это откроет конфиг для модуля.",
    }

    all_strings = {
        "strings": strings,
        "strings_en": strings,
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
        self._lib_classname = self.apo_lib.__class__.__name__
        self._lib_db = self._db[self._lib_classname]
        self._chats_db = self._lib_db.setdefault("chats", {})
        if self.apo_lib._controllerloader.unload_controller:
            self.apo_lib._controllerloader.unload_controller = False

    async def capolibcmd(self, message: Message):
        """
        This will open the config for the module.
        """
        await self.allmodules.commands["config"](
            await utils.answer(
                message, f"{self.get_prefix()}config {self._lib_classname}"
            )
        )

    async def unloadapocontrollercmd(self, message: Message):
        """
        This will unload the module and prevent it from loading through apo_lib.
        !!Beware that this will break all modules that depend on apo_lib q_watcher. Use this only if you know what you are doing!!
        """
        self.apo_lib._controllerloader.unload_controller = True
        name = self.strings("name")
        await self.allmodules.commands["unloadmod"](
            await utils.answer(message, f"{self.get_prefix()}unloadmod {name}")
        )

    async def vapolibcmd(self, message: Message):
        """
        shows the current version of the apodiktum_library.
        """
        if lib_version := getattr(self.allmodules, "_apodiktum_lib_version", None):
            version_str = f"v{lib_version[0]}.{lib_version[1]}.{lib_version[2]}"
        else:
            version_str = "v Unknown"
        await utils.answer(
            message,
            self.apo_lib.utils.get_str("version_str", self.all_strings, message).format(
                version_str
            ),
        )

    async def qapolibcmd(self, message):
        """
        shows the current queue and tasks of the apodiktum_library.
        """
        q_string = self.apo_lib.utils.get_str("queues", self.all_strings, message)
        t_string = self.apo_lib.utils.get_str("tasks", self.all_strings, message)
        tasks = "tasks="
        await asyncio.sleep(0.01)
        for name in self.apo_lib.watcher_q._watcher_q_queue:
            q_string += f"\n<code>{name}</code>"
            for q in self.apo_lib.watcher_q._watcher_q_queue[name]:
                q_string += f"\n<code> - {q}:</code>"
                q_string += self.apo_lib.utils.get_str(
                    "q_total_count", self.all_strings, message
                ).format(
                    "".join(
                        re.findall(
                            "\d+",
                            "".join(
                                s
                                for s in str(
                                    self.apo_lib.watcher_q._watcher_q_queue[name][q]
                                ).split()
                                if tasks.lower() in s.lower()
                            ),
                        )
                    )
                )
                q_string += self.apo_lib.utils.get_str(
                    "q_pending", self.all_strings, message
                ).format(self.apo_lib.watcher_q._watcher_q_queue[name][q].qsize())
        for name in self.apo_lib.watcher_q._watcher_q_task:
            t_string += f"\n<code>{name}</code>"
            for t in self.apo_lib.watcher_q._watcher_q_task[name]:
                t_string += f"\n<code> - {t}:</code> "
                t_string += self.apo_lib.utils.get_str(
                    "t_name", self.all_strings, message
                ).format(self.apo_lib.watcher_q._watcher_q_task[name][t].get_name())
                t_string += self.apo_lib.utils.get_str(
                    "t_id", self.all_strings, message
                ).format(id((self.apo_lib.watcher_q._watcher_q_task[name][t])))
                t_string += self.apo_lib.utils.get_str(
                    "t_cancelled", self.all_strings, message
                ).format(self.apo_lib.watcher_q._watcher_q_task[name][t].cancelled())
                t_string += self.apo_lib.utils.get_str(
                    "t_done", self.all_strings, message
                ).format(self.apo_lib.watcher_q._watcher_q_task[name][t].done())

        string = f"{q_string or None}\n\n{t_string or None}"
        await utils.answer(message, string)

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
        with contextlib.suppress(Exception):
            await self.apo_lib.watcher_q.msg_reciever(message)
