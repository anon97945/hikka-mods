__version__ = (0, 1, 16)


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
# scope: hikka_min 1.2.10

import logging
import random
import asyncio

import collections  # for MigratorClass
import hashlib  # for MigratorClass
import copy     # for MigratorClass

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
        "_cfg_doc_shuffle_chats": "A list of chats where the emoji list is shuffled.",
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
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_cst_auto_migrate_log": "Wheather log auto migrate as info(True) or debug(False).",
        "_cfg_cst_auto_migrate_debug": "Wheather log debug messages of auto migrate.",
    }

    strings_ru = {
        "_cfg_doc_raise_error": "Вызывает ошибку, если эмодзи не является действительным.",
        "_cfg_doc_shuffle_chats": "Список чатов, в которых перемешивается список эмодзи.",
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
            loader.ConfigValue(
                "auto_migrate_log",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate_log"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClass
            loader.ConfigValue(
                "auto_migrate_debug",
                False,
                doc=lambda: self.strings("_cfg_cst_auto_migrate_debug"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClass
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        # MigratorClass
        self._migrator = MigratorClass()  # MigratorClass define
        await self._migrator.init(client, db, self, self.__class__.__name__, self.strings("name"), self.config["auto_migrate_log"], self.config["auto_migrate_debug"])  # MigratorClass Initiate
        await self._migrator.auto_migrate_handler(self.config["auto_migrate"])
        # MigratorClass

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
                if utils.get_chat_id(message) in self.config["shuffle_reactions"]:
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


class MigratorClass():
    """
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
    """

    strings = {
        "_log_doc_migrated_db": "Migrated {} database of {} -> {}:\n{}",
        "_log_doc_migrated_cfgv_val": "[Dynamic={}] Migrated default config value:\n{} -> {}",
        "_log_doc_no_dynamic_migration": "No module config found. Did not dynamic migrate:\n{{{}: {}}}",
        "_log_doc_migrated_db_not_found": "`{}` database not found. Did not migrate {} -> {}",
    }

    changes = {
    }

    def __init__(self):
        self._ratelimit = []

    async def init(
        self,
        client: "TelegramClient",  # type: ignore
        db: "Database",  # type: ignore
        modules: str,  # type: ignore
        classname: str,  # type: ignore
        name: str,  # type: ignore
        log: bool = False,  # type: ignore
        debug: bool = False,  # type: ignore
    ):
        self._client = client
        self._db = db
        self._classname = classname
        self._name = name
        self.modules = modules
        self.log = log
        self.debug = debug
        self.hashs = []
        self.hashs = self._db.get(self._classname, "hashs", [])
        self._migrate_to = list(self.changes)[-1] if self.changes else None

    async def migrate(self, log: bool = False, debug: bool = False):
        self.log = log
        self.debug = debug
        if self._migrate_to is not None:
            self.hashs = self._db.get(self._classname, "hashs", [])

            migrate = await self.check_new_migration()
            full_migrated = await self.full_migrated()
            if migrate:
                await self._logger(f"Open migrations: {migrate}", self.debug, True)
                if await self._migrator_func():
                    await self._logger("Migration done.", self.debug, True)
                    return True
            elif not full_migrated:
                await self.force_set_hashs()
                await self._logger(f"Open migrations: {migrate} | Forcehash done: {self.hashs}", self.debug, True)
                return False
            else:
                await self._logger(f"Open migrations: {migrate} | Skip migration.", self.debug, True)
                return False
            return False
        await self._logger("No changes in `changes` dictionary found.", self.debug, True)
        return False

    async def auto_migrate_handler(self, auto_migrate: bool = False):
        if self._migrate_to is not None:
            self.hashs = self._db.get(self._classname, "hashs", [])
            migrate = await self.check_new_migration()
            full_migrated = await self.full_migrated()
            if auto_migrate and migrate:
                await self._logger(f"Open migrations: {migrate} | auto_migrate: {auto_migrate}", self.debug, True)
                if await self._migrator_func():
                    await self._logger("Migration done.", self.debug, True)
                    return
            elif not auto_migrate and not full_migrated:
                await self.force_set_hashs()
                await self._logger(f"Open migrations: {migrate} | auto_migrate: {auto_migrate} | Forcehash done: {self.hashs}", self.debug, True)
                return
            else:
                await self._logger(f"Open migrations: {migrate} | auto_migrate: {auto_migrate} | Skip migrate_handler.", self.debug, True)
                return
        await self._logger("No changes in `changes` dictionary found.", self.debug, True)
        return

    async def force_set_hashs(self):
        await self._set_missing_hashs()
        return True

    async def check_new_migration(self):
        chash = hashlib.sha256(self._migrate_to.encode('utf-8')).hexdigest()
        return chash not in self.hashs

    async def full_migrated(self):
        full_migrated = True
        for migration in self.changes:
            chash = hashlib.sha256(migration.encode('utf-8')).hexdigest()
            if chash not in self.hashs:
                full_migrated = False
        return full_migrated

    async def _migrator_func(self):
        for migration in self.changes:
            chash = hashlib.sha256(migration.encode('utf-8')).hexdigest()
            if chash not in self.hashs:
                old_classname, new_classname, old_name, new_name = await self._get_names(migration)
                for category in self.changes[migration]:
                    await self._copy_config_init(migration, old_classname, new_classname, old_name, new_name, category)
                await self._set_hash(chash)
        return True

    async def _copy_config_init(self, migration, old_classname, new_classname, old_name, new_name, category):
        if category == "classname":
            if self._classname != old_classname and (old_classname in self._db.keys() and self._db[old_classname] and old_classname is not None):
                await self._logger(f"{migration} | {category} | old_value: {str(old_classname)} | new_value: {str(new_classname)}", self.debug, True)
                await self._copy_config(category, old_classname, new_classname, new_name)
            else:
                await self._logger(self.strings["_log_doc_migrated_db_not_found"].format(category, old_classname, new_classname))
        elif category == "name":
            await self._logger(f"{migration} | {category} | old_value: {str(old_name)} | new_value: {str(new_name)}", self.debug, True)
            if self._name != old_name and (old_name in self._db.keys() and self._db[old_name] and old_name is not None):
                await self._copy_config(category, old_name, new_name, new_classname)
            else:
                await self._logger(self.strings["_log_doc_migrated_db_not_found"].format(category, old_name, new_name))
        elif category == "config":
            await self._migrate_cfg_values(migration, category, new_name, new_classname)
        return

    async def _get_names(self, migration):
        old_name = None
        old_classname = None
        new_name = None
        new_classname = None
        for category in self.changes[migration]:
            if category == "classname":
                old_classname, new_classname = await self._get_changes(self.changes[migration][category].items())
            elif category == "name":
                old_name, new_name = await self._get_changes(self.changes[migration][category].items())
        if not new_name:
            new_name = self._name
        if not new_classname:
            new_classname = self._classname
        return old_classname, new_classname, old_name, new_name

    @staticmethod
    async def _get_changes(changes):
        old_value = None
        new_value = None
        for state, value in changes:
            if state == "old":
                old_value = value
            elif state == "new":
                new_value = value
        return old_value, new_value

    async def _migrate_cfg_values(self, migration, category, new_name, new_classname):
        if new_classname in self._db.keys() and "__config__" in self._db[new_classname]:
            if configdb := self._db[new_classname]["__config__"]:
                for cnfg_key in self.changes[migration][category]:
                    old_value, new_value = await self._get_changes(self.changes[migration][category][cnfg_key].items())
                    for key, value in configdb.items():
                        await self._logger(f"{migration} | {category} | ({{old_value: {str(old_value)}}} `==` {{new_value: {str(value)}}}) `and` {{key: {key}}} `==` {{cnfg_key: {cnfg_key}}}", self.debug, True)
                        if value == old_value and key == cnfg_key:
                            dynamic = False
                            self._db[new_classname]["__config__"][cnfg_key] = new_value
                            if (
                                self.modules.lookup(new_name)
                                and self.modules.lookup(new_name).config
                                and key in self.modules.lookup(new_name).config
                            ):
                                self.modules.lookup(new_name).config[cnfg_key] = new_value
                                dynamic = True
                            await self._logger(self.strings["_log_doc_migrated_cfgv_val"].format(dynamic, value, new_value))
        return

    async def _copy_config(self, category, old_name, new_name, name):
        if self._db[new_name]:
            temp_db = {new_name: copy.deepcopy(self._db[new_name])}
            self._db[new_name].clear()
            self._db[new_name] = await self._deep_dict_merge(temp_db[new_name], self._db[old_name])
            temp_db.pop(new_name)
        else:
            self._db[new_name] = copy.deepcopy(self._db[old_name])
        self._db.pop(old_name)
        await self._logger(self.strings["_log_doc_migrated_db"].format(category, old_name, new_name, self._db[new_name]))
        if category == "classname":
            await self._make_dynamic_config(name, new_name)
        if category == "name":
            await self._make_dynamic_config(new_name, name)
        return

    async def _deep_dict_merge(self, dct1, dct2, override=True) -> dict:
        merged = copy.deepcopy(dct1)
        for k, v2 in dct2.items():
            if k in merged:
                v1 = merged[k]
                if isinstance(v1, dict) and isinstance(v2, collections.abc.Mapping):
                    merged[k] = await self._deep_dict_merge(v1, v2, override)
                elif isinstance(v1, list) and isinstance(v2, list):
                    merged[k] = v1 + v2
                elif override:
                    merged[k] = copy.deepcopy(v2)
            else:
                merged[k] = copy.deepcopy(v2)
        return merged

    async def _make_dynamic_config(self, new_name, new_classname=None):
        if new_classname is None:
            return
        if "__config__" in self._db[new_classname].keys():
            for key, value in self._db[new_classname]["__config__"].items():
                if (
                    self.modules.lookup(new_name)
                    and self.modules.lookup(new_name).config
                    and key in self.modules.lookup(new_name).config
                ):
                    self.modules.lookup(new_name).config[key] = value
                else:
                    await self._logger(self.strings["_log_doc_no_dynamic_migration"].format(key, value))
        return

    async def _set_hash(self, chash):
        self.hashs.append(chash)
        self._db.set(self._classname, "hashs", self.hashs)
        return

    async def _set_missing_hashs(self):
        for migration in self.changes:
            chash = hashlib.sha256(migration.encode('utf-8')).hexdigest()
            if chash not in self.hashs:
                await self._set_hash(chash)

    async def _logger(self, log_string, debug: bool = False, debug_msg: bool = False):
        if not debug_msg and self.log:
            return logger.info(log_string)
        if debug and debug_msg:
            return logger.info(log_string)
        return logger.debug(log_string)
