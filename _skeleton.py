__version__ = (0, 0, 21)


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

import logging

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumSkeletonMod(loader.Module):
    """
    This is a skeleton module.
    """

    strings = {
        "name": "Apo-Skeleton",
        "developer": "@anon97945",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_skel_bool": "This is a skeleton boolean config.",
        "_cfg_skel_series": "This is a skeleton series config.",
        "_cfg_skel_union": "This is a skeleton union config.",
        "_cfg_translation_chats": "Define Chats where the translation is forced.",
        "_cmd_skeleton": "This is a skeleton command.",
        "no_args": "No args are given...",
        "no_int": "Your input was no Integer.",
        "skeleton_argmsg": "This is a skeleton message with args.\n{}",
        "skeleton_msg": "This is a skeleton message.",
    }

    strings_en = {}

    strings_de = {
        "_cfg_skel_bool": "Dies ist ein Skeleton Boolean Config.",
        "_cfg_skel_series": "Dies ist ein Skeleton Series Config.",
        "_cfg_skel_union": "Dies ist ein Skeleton Union Config.",
        "_cfg_translation_chats": "Definiere Chats, wo die Übersetzung erzwungen wird.",
        "_cmd_doc_cskeleton": "Dadurch wird die Konfiguration für das Modul geöffnet.",
        "_cmd_doc_skeleton": "Dies ist ein Skeleton Command.",
        "_cmd_doc_skeletonargs": "Dies ist ein Skeleton Command mit Argumenten.",
        "no_args": "Keine Argumente angegeben...",
        "no_int": "Dein Eingabe war keine Integer.",
        "skeleton_argmsg": "Dies ist ein Skeleton Nachricht mit Argumenten.\n{}",
        "skeleton_msg": "Dies ist ein Skeleton Nachricht.",
    }

    strings_ru = {
        "_cfg_skel_bool": "Это скелетная булевая конфигурация.",
        "_cfg_skel_series": "Это скелетная конфигурация с сериями.",
        "_cfg_skel_union": "Это скелетная конфигурация с объединением.",
        "_cfg_translation_chats": "Задать чаты, где применяется перевод.",
        "_cls_doc": "Это скелетный модуль.",
        "_cmd_doc_cskeleton": "Это откроет конфиг для модуля.",
        "_cmd_doc_skeleton": "Это скелетная команда.",
        "_cmd_doc_skeletonargs": "Это скелетное сообщение с аргументами.",
        "no_args": "ргументы не указаны...",
        "no_int": "Ваш ввод не является целочисленным типом (int)",
        "skeleton_argmsg": "Это команда с аргументами.\n{}",
        "skeleton_msg": "Это скелетное сообщение.",
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
                "old": "Apo Skeleton",
                "new": "Apo-Skeleton",
            },
        },
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "skeleton_bool",
                True,
                doc=lambda: self.strings("_cfg_skel_bool"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "skeleton_union",
                "None",
                doc=lambda: self.strings("_cfg_skel_union"),
                validator=loader.validators.Union(
                    loader.validators.Float(minimum=0, maximum=600),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "skeleton_series",
                [123, 456, 789],
                doc=lambda: self.strings("_cfg_skel_series"),
                validator=loader.validators.Series(
                    loader.validators.TelegramID(),
                ),
            ),
            loader.ConfigValue(
                "auto_migrate",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClas
        )

    async def client_ready(self):
        self.apo_lib = await self.import_lib(
            "https://raw.githubusercontent.com/anon97945/hikka-libs/master/apodiktum_library.py",
            suspend_on_error=True,
        )
        await self.apo_lib.migrator.auto_migrate_handler(
            self.__class__.__name__,
            self.strings("name"),
            self.changes,
            self.config["auto_migrate"],
        )
        self.apo_lib.watcher_q.register(
            self.__class__.__name__, "q_watcher1"
        )  # Register the q_watcher1; name is optional if you only have one watcher (q_watcher is the default name)

    async def on_unload(self):
        self.apo_lib.watcher_q.unregister(
            self.__class__.__name__, "q_watcher1"
        )  # Unregister the q_watcher1; name is necessary if you registered the watcher with a name. Must match the name you registered the watcher with
        return

    async def on_dlmod(self, client, _):
        return

    async def cskeletoncmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def skeletoncmd(self, message):
        """
        This is a skeleton command.
        """
        await utils.answer(
            message,
            self.apo_lib.utils.get_str("skeleton_msg", self.all_strings, message),
        )
        return

    async def skeletoargscmd(self, message):
        """
        This is a skeleton command with args.
        """
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_args", self.all_strings, message),
            )
            return
        if not self.apo_lib.utils.validate_integer(args[0]):
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_int", self.all_strings, message),
            )
            return
        await utils.answer(
            message,
            self.apo_lib.utils.get_str(
                "skeleton_argmsg", self.all_strings, message
            ).format(args),
        )

    async def q_watcher1(self, message: Message):
        """
        This is the watcher function. Name must be the same as the one you registered the q_watcher with
        """
        return

    async def watcher(self, message):
        """
        This is a watcher.
        """
        return
