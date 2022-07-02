__version__ = (1, 0, 11)


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
import asyncio

import collections  # for MigratorClass
import hashlib  # for MigratorClass
import copy     # for MigratorClass

from .. import loader, utils
from telethon.tl.types import Message

logger = logging.getLogger(__name__)
skip_update = ["[do not install]", "[unstable]", "[test]"]


async def buttonhandler(bmsg, chatid, caption1, caption2, data_btn1, data_btn2):
    fnd_btn1 = False
    fnd_btn2 = False
    bmsg = await bmsg.client.get_messages(chatid, ids=bmsg.id)
    buttons = bmsg.buttons
    if (
        caption1 in bmsg.message or caption2 in bmsg.message
    ) and bmsg.buttons is not None:
        for row in buttons:
            for button in row:
                if data_btn1 in str(button.data):
                    fnd_btn1 = True
                if data_btn2 in str(button.data):
                    fnd_btn2 = True
                if fnd_btn1 and fnd_btn2:
                    return True
    return False


@loader.tds
class ApodiktumAutoUpdateMod(loader.Module):
    """
    Automatically update your Hikka Userbot
    """
    strings = {
        "name": "Apo AutoUpdater",
        "developer": "@anon97945",
        "_cfg_auto_update": "Whether the Hikka Userbot should automatically update or not.",
        "_cfg_auto_update_delay": "Choose a delay to wait to start the automatic update.",
        "_cfg_update_msg_read": "Whether to mark the message as read or not.",
        "_cfg_update_skip": "The update was skipped due to {}.\n{}",
        "updating": ("Hikka Userbot will be automatically updated in {} seconds.\n\n"
                     "Changelog:\n{}"),
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_cst_auto_migrate_log": "Wheather log auto migrate as info(True) or debug(False).",
        "_cfg_cst_auto_migrate_debug": "Wheather log debug messages of auto migrate.",
    }

    strings_de = {
        "_cfg_auto_update": "Ob der Hikka Userbot automatisch aktualisieren soll oder nicht.",
        "_cfg_auto_update_delay": "Wählen Sie eine Wartezeit bis zum Start des automatischen Updates.",
        "_cfg_update_msg_read": "Ob die Nachricht als gelesen markiert werden soll oder nicht.",
        "_cfg_update_skip": "Das Update wurde wegen {} übersprungen.\n{}",
        "_cmd_doc_cautoupdate": "Dadurch wird die Konfiguration für das Modul geöffnet.",
        "updating": ("Hikka Userbot wird in {} Sekunden automatisch aktualisiert.\n\n"
                     "Changelog:\n{}"),
    }

    strings_ru = {
        "_cfg_auto_update": "Должен ли Hikka UserBot обновляться автоматически или нет.",
        "_cfg_auto_update_delay": "Выберите задержку для автоматического обновления.",
        "_cfg_update_msg_read": "Будет ли отмечать сообщение обновления как прочтённое или нет.",
        "_cfg_update_skip": "Обновление было пропущено из-за {}.\n{}",
        "_cmd_doc_cautoupdate": "Это откроет конфиг для модуля.",
        "updating": ("Хикка будет автоматически обновлена через {} секунд.\n\n"
                     "Список изменений:\n{}"),
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "auto_update",
                "True",
                doc=lambda: self.strings("_cfg_auto_update"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "mark_read",
                "True",
                doc=lambda: self.strings("_cfg_update_msg_read"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "update_delay",
                "600",
                doc=lambda: self.strings("_cfg_auto_update_delay"),
                validator=loader.validators.Integer(minimum=60),
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

    async def cautoupdatecmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def _autoupdate(self, message):
        changes = "\n".join(message.raw_text.splitlines()[5:])
        if self.config["mark_read"]:
            await self._client.send_read_acknowledge(
                message.chat_id,
                clear_mentions=True,
            )

        logger.info(self.strings("updating").format(self.config["update_delay"], changes))
        await asyncio.sleep(self.config["update_delay"])
        try:
            return await message.click(0)
        except Exception:
            return

    async def _check_skip(self, message):
        last_commit = message.raw_text.splitlines()[5].lower()
        for x in skip_update:
            if (
                x.lower() in last_commit
                and "revert" not in last_commit
            ):
                logger.info(self.strings("_cfg_update_skip").format(x, last_commit))
                return True
        return False

    async def _check_on_load(self, client):
        if self.config["auto_update"]:
            async for message in client.iter_messages(entity=self.inline.bot_id,
                                                      limit=5):
                if (
                    isinstance(message, Message)
                    and message.sender_id == self.inline.bot_id
                    and await buttonhandler(
                        message,
                        self.inline.bot_id,
                        "🌘 Hikka Update available!",
                        "🌘 Доступно обновление Hikka!",
                        "hikka_update",
                        "hikka_upd_ignore",
                    )
                ):
                    if await self._check_skip(message):
                        return
                    return await self._autoupdate(message)

    async def client_ready(self, client, db):
        self._db = db
        asyncio.ensure_future(self._check_on_load(client))
        # MigratorClass
        self._migrator = MigratorClass()  # MigratorClass define
        await self._migrator.init(client, db, self, self.__class__.__name__, self.strings("name"), self.config["auto_migrate_log"], self.config["auto_migrate_debug"])  # MigratorClass Initiate
        await self._migrator.auto_migrate_handler(self.config["auto_migrate"])
        # MigratorClass

    async def watcher(self, message: Message):
        if (
            isinstance(message, Message)
            and self.config["auto_update"]
            and utils.get_chat_id(message) == self.inline.bot_id
            and message.sender_id == self.inline.bot_id
            and message.is_private
            and await buttonhandler(
                message,
                self.inline.bot_id,
                "🌘 Hikka Update available!",
                "🌘 Доступно обновление Hikka!",
                "hikka_update",
                "hikka_upd_ignore",
            )
        ):
            if await self._check_skip(message):
                return
            return await self._autoupdate(message)


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
        logger.error(f"Log: {self.log} | Debug: {self.debug}")
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
                if isinstance(v1, dict) and isinstance(v2, collections.Mapping):
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
