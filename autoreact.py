__version__ = (0, 1, 30)


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
import logging
import random

from telethon.errors import ReactionInvalidError
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumAutoReactMod(loader.Module):
    """
    AutoReact to messages.
    Check the `.config apodiktum autoreact`
    """

    strings = {
        "name": "Apo-AutoReact",
        "developer": "@anon97945",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_doc_delay": "The delay between reactions are send in seconds.",
        "_cfg_doc_delay_chats": (
            "List of delay chats.\nIf the chat is in the list, the delay is used."
        ),
        "_cfg_doc_ignore_self": "Do not react to messages from yourself.",
        "_cfg_doc_raise_error": "Raise an error if the emoji is not valid.",
        "_cfg_doc_random_delay": (
            "Randomizes the delay between reactions. Randomness is between 0"
            " and the global delay."
        ),
        "_cfg_doc_random_delay_chats": (
            "List of random delay chats.\nIf the chat is in the list, a random"
            " delay is used."
        ),
        "_cfg_doc_reactions": (
            "Setup AutoReact.\nYou can define alternative emojis to react with, when"
            " the Chat doesn't allow the first, second etc.\nYou can also define an all"
            " OR global state, which will either apply reactions to all chat members"
            " (all) or to one user in all groups(global).\nYou can't use both at the"
            " same time! Does also work for channels! You need to use"
            " ALL!\n\nPattern:\n<userid/all>|<chatid/global>|<emoji1>|<emoji2>|<emoji3>...\n\nExample:\nall|1792410946|❤️|👍|🔥\nFor"
            " Channels:\nall|<channelid>|❤️|👍|🔥"
        ),
        "_cfg_doc_reactions_chance": (
            "The chance of reacting to a message.\n0.0 is the chance of not"
            " reacting to"
            " a message.\n1.0 is the chance of reacting to a message every"
            " time."
            "Pattern:\n<userid/all>|<chatid/global>|<percentage(0.00-1)>\n\nExample:\n1234567|global|0.8"
        ),
        "_cfg_doc_shuffle_chats": "A list of chats where the emoji list is shuffled.",
    }

    strings_en = {}

    strings_de = {}

    strings_ru = {
        "_cfg_doc_delay": "Задержка между реакциями в секундах",
        "_cfg_doc_delay_chats": (
            "Список чатов с задержкой.\nЕсли чат находится в списке, то"
            " используется задержка."
        ),
        "_cfg_doc_ignore_self": "Не ставить реакции на свои сообщения",
        "_cfg_doc_raise_error": "Вызывает ошибку, если эмодзи неверный.",
        "_cfg_doc_random_delay": (
            "Случайным образом изменяет задержку между реакциями. Вероятность"
            " находится в диапазоне от 0 до глобальной задержки."
        ),
        "_cfg_doc_random_delay_chats": (
            "Список чатов со случайной задержкой.\nЕсли чат находится в списке,"
            " используется случайная задержка."
        ),
        "_cfg_doc_reactions": (
            "Настройка автореакции.\nВы можете указать альтернативные эмодзи для"
            " реакций. Будет выбран первый доступный в чате\nВы также можете определить"
            " состояние все(all) или глобальное(global) которое будет применять реакцию"
            " либо ко всем участникам чата (все), либо к одному пользователю во всех"
            " группах (глобальное).\nВы не можете использовать оба варианта"
            " одновременно! Это также работает для каналов! Вам нужно использовать"
            " ALL!\n\nФормат:\n<userid/all>|<chatid/global>|<emoji1>|<emoji2>|<emoji3>...\n\nПример:\nall|1792410946|❤️|👍|🔥\nДля"
            " каналов:\nall|<channelid>|❤️|👍|🔥"
        ),
        "_cfg_doc_reactions_chance": (
            "Шанс реакции на сообщение.\n0.0 - всегда не реагировать на"
            " сообщение.\n1.0 -"
            " всегда реагировать на сообщение."
            "Формат:\n<userid/all>|<chatid/global>|<percentage(0.00-1)>\n\nПример:\n1234567|global|0.8"
        ),
        "_cfg_doc_shuffle_chats": (
            "Список чатов, в которых перемешивается список эмодзи."
        ),
        "_cls_doc": "Автореакция на сообщения.\nПроверьте .config apodiktum autoreact.",
        "_cmd_doc_cautoreact": "Это откроет конфиг для модуля.",
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
                "old": "Apo AutoReact",
                "new": "Apo-AutoReact",
            },
        },
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "reaction_active",
                True,
                doc=lambda: self.strings("_cfg_doc_react"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "delay",
                0.5,
                doc=lambda: self.strings("_cfg_doc_delay"),
                validator=loader.validators.Union(
                    loader.validators.Float(minimum=0, maximum=600),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "delay_chats",
                doc=lambda: self.strings("_cfg_doc_delay_chats"),
                validator=loader.validators.Series(
                    loader.validators.TelegramID(),
                ),
            ),
            loader.ConfigValue(
                "ignore_self",
                False,
                doc=lambda: self.strings("_cfg_doc_ignore_self"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "raise_error",
                False,
                doc=lambda: self.strings("_cfg_doc_raise_error"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "random_delay_chats",
                doc=lambda: self.strings("_cfg_doc_random_delay_chats"),
                validator=loader.validators.Series(
                    loader.validators.TelegramID(),
                ),
            ),
            loader.ConfigValue(
                "reactions",
                ["all|1792410946|❤️|👍|🔥"],
                doc=lambda: self.strings("_cfg_doc_reactions"),
                validator=loader.validators.Series(
                    validator=loader.validators.RegExp(
                        r"^(?:(?:\d+)[|](?:\d+|global)|(?:\d+|all)[|]\d+)(?:[|][👍👎❤️🔥🥰👏😁🤔🤯😱🤬😢🎉🤩🤮💩🙏👌🕊🤡🥱🥴😍🐳❤️‍🔥🌚🌭💯🤣⚡️🍌🏆💔🤨😐🍓🍾💋🖕😈😴😭🤓👻👨‍💻👀🎃🙈😇😨🤝✍️🤗🫡🎅🎄☃️💅🤪🗿🆒💘🙉😎👾🤷‍♂️🤷🤷‍♀️😡]|[|][\u2764])+"
                    )
                ),
            ),
            loader.ConfigValue(
                "reactions_chance",
                doc=lambda: self.strings("_cfg_doc_reactions_chance"),
                validator=loader.validators.Series(
                    validator=loader.validators.RegExp(
                        r"^(?:(?:\d+)[|](?:\d+|global)|(?:\d+|all)[|]\d+)(?:[|](?:0(?:\.\d{1,2})?|1(?:\.0{1,2})?))$"
                    )
                ),
            ),
            loader.ConfigValue(
                "shuffle_reactions",
                doc=lambda: self.strings("_cfg_doc_shuffle_chats"),
                validator=loader.validators.Series(
                    loader.validators.TelegramID(),
                ),
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
        await self.apo_lib.migrator.auto_migrate_handler(
            self.__class__.__name__,
            self.strings("name"),
            self.changes,
            self.config["auto_migrate"],
        )

    async def cautoreactcmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    @loader.watcher("only_messages")
    async def watcher(self, message: Message):
        if not self.config["reaction_active"]:
            return
        reactions = self.config["reactions"]
        reactions_chance = self.config["reactions_chance"]

        for reaction in reactions:
            userid, chatid, *emoji_list = reaction.split("|")
            if userid == "all" and chatid == "global":
                return
            if (
                (str(message.sender_id) == userid or userid == "all")
                and (str(utils.get_chat_id(message)) == chatid or chatid == "global")
                and not (userid == "all" and self.config["ignore_self"] and message.out)
            ):
                if not await self._reactions_chance(reactions_chance, message):
                    return
                if utils.get_chat_id(message) in self.config["shuffle_reactions"]:
                    emoji_list = random.sample(emoji_list, len(emoji_list))
                await self._delay(chatid, userid)
                for emoji_reaction in emoji_list:
                    if await self._react_message(message, emoji_reaction, chatid):
                        return

    async def _delay(self, chatid, userid):
        if chatid != "global":
            chatid = int(chatid)
        if userid != "all":
            userid = int(userid)
        if (
            chatid in self.config["delay_chats"]
            or userid in self.config["delay_chats"]
            or chatid in self.config["random_delay_chats"]
            or userid in self.config["random_delay_chats"]
        ):
            if (
                chatid not in self.config["random_delay_chats"]
                or userid not in self.config["random_delay_chats"]
            ):
                await asyncio.sleep(self.config["delay"])
            else:
                await asyncio.sleep(round(random.uniform(0, self.config["delay"]), 2))

    @staticmethod
    async def _reactions_chance(reactions_chance: list, message: Message) -> bool:
        for r_chance in reactions_chance:
            userid, chatid, chance = r_chance.split("|")
            if userid == "all" and chatid == "global":
                return False
            if (
                (str(message.sender_id) == userid or userid == "all")
                and (str(utils.get_chat_id(message)) == chatid or chatid == "global")
                and random.random() > float(chance)
            ):
                return False
        return True

    async def _react_message(
        self,
        message: Message,
        emoji_reaction: str,
        chatid: int,
    ) -> bool:
        try:
            await message.react(emoji_reaction)
            return True
        except ReactionInvalidError:
            if self.config["raise_error"]:
                self.apo_lib.utils.log(
                    logging.INFO,
                    __name__,
                    f"ReactionInvalidError: {emoji_reaction} in chat {chatid}",
                )
            return False
        except Exception as exc:  # skipcq: PYL-W0703
            if self.config["raise_error"]:
                if "PREMIUM_ACCOUNT_REQUIRED" in str(exc):
                    self.apo_lib.utils.log(
                        logging.INFO,
                        __name__,
                        f"PREMIUM_ACCOUNT_REQUIRED: {emoji_reaction} in chat {chatid}",
                    )
                else:
                    self.apo_lib.utils.log(logging.INFO, __name__, f"Error: {exc}")
            return False
