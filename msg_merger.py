__version__ = (0, 0, 15)


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

import logging
from datetime import datetime, timezone

import collections  # for MigratorClass
import hashlib  # for MigratorClass
import copy     # for MigratorClass

from emoji import UNICODE_EMOJI
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumMsgMergerMod(loader.Module):
    """
    This module will merge own messages, if there is no message in between.
    """

    strings = {
        "name": "Apo MsgMerger",
        "developer": "@anon97945",
        "_cfg_active": "Whether the module is turned on (or not).",
        "_cfg_blacklist_chats": "The list of chats that the module will watch(or not).",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_cst_auto_migrate_debug": "Wheather log debug messages of auto migrate.",
        "_cfg_cst_auto_migrate_log": "Wheather log auto migrate as info(True) or debug(False).",
        "_cfg_edit_timeout": "The maximum time in minuted to edit the message. 0 for no limit.",
        "_cfg_new_lines": "The number of new lines to add to the message.",
        "_cfg_skip_emoji": "Whether to skip the merging of messages with single emoji.",
        "_cfg_skip_length": "The length of the message to skip the merging.",
        "_cfg_skip_prefix": "The prefix to skip the merging.",
        "_cfg_skip_reply": "Whether to skip the merging of messages with reply.",
        "_cfg_whitelist": "Whether the chatlist includes(True) or excludes(False) the chat.",
        "_cfg_merge_own_reply": "Whether to merge any message from own reply.",
        "_cfg_merge_own_reply_msg": "The message which will stay if the message is merged from own reply. ",
    }

    strings_en = {
    }

    strings_de = {
    }

    strings_ru = {
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "active",
                "True",
                doc=lambda: self.strings("_cfg_active"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "chatlist",
                doc=lambda: self.strings("_cfg_blacklist_chats"),
                validator=loader.validators.Series(
                    loader.validators.TelegramID()
                ),
            ),
            loader.ConfigValue(
                "edit_timeout",
                2,
                doc=lambda: self.strings("_cfg_edit_timeout"),
                validator=loader.validators.Union(
                    loader.validators.Integer(minimum=1),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "merge_own_reply",
                False,
                doc=lambda: self.strings("_cfg_merge_own_reply"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "new_line_pref",
                ">",
                doc=lambda: self.strings("_cfg_new_line_prefix"),
                validator=loader.validators.Union(
                    loader.validators.String(length=1),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "new_lines",
                1,
                doc=lambda: self.strings("_cfg_new_lines"),
                validator=loader.validators.Integer(minimum=1, maximum=2),
            ),
            loader.ConfigValue(
                "own_reply_msg",
                "<code>☝️</code>",
                doc=lambda: self.strings("_cfg_merge_own_reply_msg"),
                validator=loader.validators.Union(
                    loader.validators.String(),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "skip_emoji",
                True,
                doc=lambda: self.strings("_cfg_skip_emoji"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "skip_length",
                doc=lambda: self.strings("_cfg_skip_length"),
                validator=loader.validators.Union(
                    loader.validators.Integer(minimum=0),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "skip_prefix",
                ">",
                doc=lambda: self.strings("_cfg_skip_prefix"),
                validator=loader.validators.Union(
                    loader.validators.String(length=1),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "skip_reply",
                False,
                doc=lambda: self.strings("_cfg_skip_reply"),
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

    @staticmethod
    def is_emoji(text):
        count = 0
        for lang in UNICODE_EMOJI:
            for emoji in UNICODE_EMOJI[lang]:
                if emoji in text:
                    count += 1
                    break
        return bool(count)

    async def cmsgmergercmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def watcher(self, message):
        if (
            not self.config["active"]
            or not isinstance(message, Message)
            or message.sender_id != self._tg_id
            or message.media
            or message.via_bot
            or message.fwd_from
            or utils.remove_html(message.text)[0] == self.get_prefix()
        ):
            return

        chatid = utils.get_chat_id(message)

        if (
            (
                self.config["whitelist"]
                and chatid not in self.config["chatlist"]
            )
            or (
                not self.config["whitelist"]
                and chatid in self.config["chatlist"]
            )
        ):
            return

        skip_prefix_len = len(utils.escape_html(self.config["skip_prefix"]))
        if (
            self.config["skip_prefix"]
            and utils.remove_html(message.text)[:skip_prefix_len] == utils.escape_html(self.config["skip_prefix"])
        ):
            text = message.text.replace(utils.escape_html(self.config["skip_prefix"]), "")
            await message.edit(text)
            return

        if (
            self.config["skip_length"]
            and len(utils.remove_html(message.text)) >= self.config["skip_length"]
        ):
            return

        for i in range(-4, -1):
            last_msg = (await self._client.get_messages(chatid, limit=5))[i]
            if last_msg.id != message.id:
                break

        if self.config["merge_own_reply"] and message.is_reply:
            last_msg = await message.get_reply_message()

        if (
            (
                self.config["skip_emoji"]
                and (
                    self.is_emoji(message.text)
                    or self.is_emoji(last_msg.text)
                )
                and (
                    len(message.text) == 1
                    or len(last_msg.text) == 1
                )
            )
            or (
                self.config["skip_reply"]
                and not self.config["merge_own_reply"]
                and (
                    message.is_reply
                    or last_msg.is_reply
                )
            )
            or (
                last_msg.is_reply and message.is_reply and not self.config["merge_own_reply"]
            )
        ):
            return

        if(
            last_msg.sender_id != self._tg_id
            or not isinstance(last_msg, Message)
            or last_msg.media
            or last_msg.via_bot
            or last_msg.fwd_from
            or utils.remove_html(last_msg.text)[0] == self.get_prefix()
        ):
            return

        if (
            self.config["edit_timeout"]
            and (datetime.now(timezone.utc) - (last_msg.edit_date or last_msg.date)).total_seconds() > self.config["edit_timeout"] * 60
            and not self.config["merge_own_reply"]
        ):
            return

        text = last_msg.text
        text += "\n" * self.config["new_lines"]

        if self.config["new_line_pref"]:
            text += self.config["new_line_pref"]
        text += message.text

        if message.is_reply and not self.config["merge_own_reply"]:
            message, last_msg = last_msg, message
        try:
            msg = await last_msg.edit(text)
            if msg.out:
                if self.config["merge_own_reply"] and self.config["own_reply_msg"] and message.is_reply:
                    await message.edit(self.config["own_reply_msg"])
                    return
                await message.delete()
                return
        except Exception as e:
            logger.debug(f"Edit last_msg:\n{str(e)}")
            return


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
