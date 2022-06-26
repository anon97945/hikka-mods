__version__ = (0, 0, 1)


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
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @apodiktum_modules

# scope: hikka_only
# scope: hikka_min 1.1.28

import logging

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


def represents_int(s: str) -> bool:
    try:
        loader.validators.Integer().validate(s)
        return True
    except loader.validators.ValidationError:
        return False


@loader.tds
class ApodiktumSkeletonMod(loader.Module):
    """
    This is a skeleton module.
    """

    strings = {
        "name": "Apo Skeleton",
        "developer": "@anon97945",
        "_cfg_skel_bool": "This is a skeleton boolean config.",
        "_cfg_skel_series": "This is a skeleton series config.",
        "_cfg_skel_union": "This is a skeleton union config.",
        "_cmd_skeleton": "This is a skeleton command.",
        "no_args": "No args are given...",
        "no_int": "Your input was no Integer.",
        "skeleton_argmsg": "This is a skeleton message with args.\n{}",
        "skeleton_msg": "This is a skeleton message.",
    }

    strings_ru = {
        "_cfg_skel_bool": "Это скелетная булевая конфигурация.",
        "_cfg_skel_series": "Это скелетная конфигурация с сериями.",
        "_cfg_skel_union": "Это скелетная конфигурация с объединением.",
        "_cls_doc": "Это скелетный модуль.",
        "_cmd_doc_cadmintools": "Это откроет конфиг для модуля.",
        "_cmd_skeletoargs": "Это команда с аргументами.\n{}",
        "_cmd_skeleton": "Это скелетная команда.",
        "no_args": "ргументы не указаны...",
        "no_int": "Ваш ввод не является целочисленным типом (int)",
        "skeleton_argmsg": "Это скелетное сообщение с аргументами.",
        "skeleton_msg": "Это скелетное сообщение.",
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "skeleton_bool",
                "True",
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
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

    async def on_unload(self):
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
        await utils.answer(message, self.strings("skeleton_msg"))
        return

    async def skeletoargscmd(self, message):
        """
        This is a skeleton command with args.
        """
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_args"))
            return
        if not represents_int(args[0]):
            await utils.answer(message, self.strings("no_int"))
            return
        await utils.answer(message, self.strings("skeleton_argmsg").format(args))

    async def watcher(self, message):
        """
        This is a watcher.
        """
        return
