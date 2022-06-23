__version__ = (0, 1, 10)

# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @apodiktum_modules

# scope: hikka_only
# scope: hikka_min 1.1.28


import logging
import random
import asyncio

from telethon.tl.types import Message
from telethon.errors import ReactionInvalidError

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumAutoReactMod(loader.Module):
    """
    AutoReact to messages.
    Check the `.config apodiktum autoreact`
    """
    strings = {
        "name": "Apo AutoReact",
        "developer": "@anon97945",
        "_cfg_doc_raise_error": "Raise an error if the emoji is not valid.",
        "_cfg_doc_shuffle": "Shuffles the list of given emojis.",
        "_cfg_doc_delay": "The delay between reactions are send in seconds.",
        "_cfg_doc_delay_chats": "List of delay chats.\nIf the chat is in the list, the delay is used.",
        "_cfg_doc_random_delay_chats": "List of random delay chats.\nIf the chat is in the list, a random delay is used.",
        "_cfg_doc_random_delay": "Randomizes the delay between reactions. Randomness is between 0 and the global delay.",
        "_cfg_doc_reactions_chance": ("The chance of reacting to a message.\n0.0 is the chance of not reacting to a message.\n1.0 is the chance of reacting to a message every time."
                                      "Pattern:\n<userid/all>|<chatid/global>|<percentage(0.00-1)>\n\nExample:\n1234567|global|0.8"),
        "_cfg_doc_reactions": ("Setup AutoReact.\nYou can define alternative emojis to react with, when the Chat doesn't allow the first, second etc.\n"
                               "You can also define an all OR global state, which will either apply reactions to all chat members (all) or to one user in all groups(global).\n"
                               "You can't use both at the same time! Does also work for channels! You need to use ALL!\n\n"
                               "Pattern:\n<userid/all>|<chatid/global>|<emoji1>|<emoji2>|<emoji3>...\n\nExample:\nall|1792410946|❤️|👍|🔥\nFor Channels:\nall|<channelid>|❤️|👍|🔥"),
    }

    strings_ru = {
        "_cfg_doc_raise_error": "Вызывает ошибку, если эмодзи не является действительным.",
        "_cfg_doc_shuffle": "Перемешивает список заданных эмодзи.",
        "_cfg_doc_delay": "Задержка между реакциями передается в секундах",
        "_cfg_doc_delay_chats": "Список чатов с задержкой.\nЕсли чат находится в списке, то используется задержка.",
        "_cfg_doc_random_delay_chats": "Список чатов со случайной задержкой.\nЕсли чат находится в списке, используется случайная задержка.",
        "_cfg_doc_random_delay": "Случайным образом изменяет задержку между реакциями. Случайность находится в диапазоне от 0 до глобальной задержки.",
        "_cfg_doc_reactions_chance": ("Шанс реакции на сообщение.\n0.0 - шанс не реагировать на сообщение.\n1.0 - шанс реагировать на сообщение каждый раз."
                                      "Pattern:\n<userid/all>|<chatid/global>|<percentage(0.00-1)>\n\nПример:\n1234567|global|0.8"),
        "_cfg_doc_reactions": ("Настройка автореакции.\nВы можете определить альтернативные эмодзи для реакции, когда чат не разрешает первый, второй и т.д.\n"
                               "Вы также можете определить состояние все(all) или глобальное(global) которое будет применять реакцию либо ко всем участникам чата (все), либо к одному пользователю во всех группах (глобальное).\n"
                               "Вы не можете использовать оба варианта одновременно! Это также работает для каналов! Вам нужно использовать ALL!\n\n"
                               "Pattern:\n<userid/all>|<chatid/global>|<emoji1>|<emoji2>|<emoji3>...\n\nПример:\nall|1792410946|❤️|👍|🔥\nДля каналов:\nall|<channelid>|❤️|👍|🔥"),
        "_cls_doc": "Автореакция на сообщения.\nПроверьте .config apodiktum autoreact.",
        "_cmd_doc_cautoreact": "Это откроет конфиг для модуля.",
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
                    validator=loader.validators.RegExp(r"^(?:(?:\d+)[|](?:\d+|global)|(?:\d+|all)[|]\d+)(?:[|][👍👎❤️🔥🥰👏😁🤔🤯😱🤬😢🎉🤩🤮💩🙏👌🕊🤡🥱🥴😍🐳🌚🌭💯🤣❤️‍🔥]|[|][\u2764])+")
                ),
            ),
            loader.ConfigValue(
                "reactions_chance",
                doc=lambda: self.strings("_cfg_doc_reactions_chance"),
                validator=loader.validators.Series(
                    validator=loader.validators.RegExp(r"^(?:(?:\d+)[|](?:\d+|global)|(?:\d+|all)[|]\d+)(?:[|](?:0(?:\.\d{1,2})?|1(?:\.0{1,2})?))$")
                ),
            ),
            loader.ConfigValue(
                "shuffle_reactions",
                True,
                doc=lambda: self.strings("_cfg_doc_shuffle"),
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

    async def cautoreactcmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def watcher(self, message: Message):
        if not isinstance(message, Message):
            return
        if not self.config["reaction_active"]:
            return
        reactions = self.config["reactions"]
        reactions_chance = self.config["reactions_chance"]

        for reaction in reactions:
            userid, chatid, *emojis = reaction.split("|")
            if userid == "all" and chatid == "global":
                return
            if (
                (str(message.sender_id) == userid or userid == "all")
                and (str(utils.get_chat_id(message)) == chatid or chatid == "global")
            ):
                if not await self._reactions_chance(reactions_chance, message):
                    return
                if self.config["shuffle_reactions"]:
                    emojis = random.sample(emojis, len(emojis))
                await self._delay(chatid, userid)
                for emoji in emojis:
                    if await self._react_message(message, emoji, chatid):
                        return

    async def _delay(self, chatid, userid):
        if chatid != "global":
            chatid = int(chatid)
        if userid != "all":
            userid = int(userid)
        if (
            chatid in self.config["delay_chats"]
            or userid in self.config["delay_chats"]
        ):
            if (
                chatid not in self.config["random_delay_chats"]
                or userid not in self.config["random_delay_chats"]
            ):
                await asyncio.sleep(self.config["delay"])
            else:
                await asyncio.sleep(round(random.uniform(0, self.config["delay"]), 2))

    @staticmethod
    async def _reactions_chance(reactions_chance, message: Message):
        for r_chance in reactions_chance:
            userid, chatid, chance = r_chance.split("|")
            if userid == "all" and chatid == "global":
                return
            if (
                (str(message.sender_id) == userid or userid == "all")
                and (
                    str(utils.get_chat_id(message)) == chatid or chatid == "global"
                )
                and random.random() > float(chance)
            ):
                return False
        return True

    async def _react_message(self, message, emoji, chatid):
        try:
            await message.react(emoji)
            return True
        except ReactionInvalidError:
            if self.config["raise_error"]:
                logger.info(f"ReactionInvalidError: {emoji} in chat {chatid}")
            return False
        except Exception as e:
            if self.config["raise_error"]:
                if "PREMIUM_ACCOUNT_REQUIRED" in str(e):
                    logger.info(f"PREMIUM_ACCOUNT_REQUIRED: {emoji} in chat {chatid}")
                else:
                    logger.info(f"Error: {e}")
            return False
