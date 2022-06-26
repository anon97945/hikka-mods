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

import json

import hashlib  # for MigratorClass
import copy     # for MigratorClass

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApoAutoMigratorMod(loader.Module):
    """
    Skeleton for MigratorClass
    """

    strings = {
        "name": "Apo-AutoMigratior",
        "developer": "@anon97945",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_cst_auto_migrate_log": "Wheather log auto migrate as info(True) or debug(False).",
        "_cfg_cst_auto_migrate_debug": "Wheather log debug messages of auto migrate.",
    }

    db_classnames = {
        "db1": "MigratorMod",
        "db2": "ApoAutoMigratorMod",
    }

    db_names = {
        "db1": "MigratorMod",
        "db2": "Apo-AutoMigratior",
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "custom_link",
                "https://t.me/link/0",
                validator=loader.validators.Link(),
            ), # for test commands
            loader.ConfigValue(
                "auto_migrate",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate"),
                validator=loader.validators.Boolean(),
            ), # for MigratorClass
            loader.ConfigValue(
                "auto_migrate_log",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate_log"),
                validator=loader.validators.Boolean(),
            ), # for MigratorClass
            loader.ConfigValue(
                "auto_migrate_debug",
                False,
                doc=lambda: self.strings("_cfg_cst_auto_migrate_debug"),
                validator=loader.validators.Boolean(),
            ), # for MigratorClass
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

        # MigratorClass
        self._migrator = MigratorClass() # MigratorClass define
        await self._migrator.init(client, db, self, self.__class__.__name__, self.strings("name"), self.config["auto_migrate_log"], self.config["auto_migrate_debug"]) # MigratorClass Initiate
        await self._migrator.auto_migrate_handler(self.config["auto_migrate"])
        # MigratorClass

        # for test commands
        self.db_classname = list(self.db_classnames.values())
        self.db_name = list(self.db_names.values())
        # for test commands


    # some test commands
    async def cmigrocmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def migratecmd(self, message: Message):
        """
        This will migrate.
        """
        if await self._migrator.migrate(self.config["auto_migrate_log"], self.config["auto_migrate_debug"]):
            await utils.answer(message, "Migrated:\n" + json.dumps(self._db))
        else:
            await utils.answer(message, "Not migrated!")

    async def resetcmd(self, message: Message):
        """
        <int|1-4>
        This will reset the module.
        """
        args = utils.get_args_raw(message)
        if await self._reset(int(args), self.db_classname[0], self.db_classname[1], self.db_name[1]):
            await utils.answer(message, f"Reset done.\nOld DB ({self.db_classname[0]}): {self._db[self.db_classname[0]]}\n\nNew DB ({self.db_classname[1]}): {self._db[self.db_classname[1]]}")
        else:
            await utils.answer(message, "no reset")

    async def getdbcmd(self, message: Message):
        """
        This will reset the module.
        """
        if self.db_classname[0] in self._db.keys():
            await utils.answer(message, f"\nOld DB ({self.db_classname[0]}): {self._db[self.db_classname[0]]}\n\nNew DB ({self.db_classname[1]}): {self._db[self.db_classname[1]]}")
        else:
            await utils.answer(message, f"\nOld DB ({self.db_classname[0]}): `None/Deleted`\n\nNew DB ({self.db_classname[1]}): {self._db[self.db_classname[1]]}")

    async def remhashscmd(self, message: Message):
        """
        This will remove the hashs.
        """
        if not await self._remhash():
            await utils.answer(message, "No hashs to remove!")
            return
        await utils.answer(message, "Removed hashs!")

    async def _remhash(self):
        try:
            self._db[self.__class__.__name__].pop("hashs")
            return True
        except KeyError:
            return False

    async def _reset(self, number: int, db1, db2, db_name2):
        if number == 1:
            self._clear_dbs(db1)
            self._default_newdb(db2, db_name2)
            self._remove_hashs(db1, db2)

            configdb = {"custom_link": "https://t.me/link/1", "auto_migrate": "False", "auto_migrate_log": "True", "auto_migrate_debug": "True"}
            self._db.set(db1, "__config__", configdb)
            return True

        if number == 2:
            self._clear_dbs(db1)
            self._default_newdb(db2, db_name2)
            self._remove_hashs(db1, db2)

            configdb = {"custom_link": "https://t.me/link/5", "auto_migrate": "False", "auto_migrate_log": "True", "auto_migrate_debug": "True"}
            self._db.set(db1, "__config__", configdb)
            return True

        if number == 3:
            self._clear_dbs(db1)
            self._default_newdb(db2, db_name2)
            self._remove_hashs(db1, db2)

            configdb = {"custom_link": "https://t.me/link/2", "auto_migrate": "False", "auto_migrate_log": "True", "auto_migrate_debug": "True"}
            self._db.set(db2, "__config__", configdb)

            self.lookup(db_name2).config["custom_link"] = "https://t.me/link/2"
            return True

        if number == 4:
            self._clear_dbs(db1)
            self._default_newdb(db2, db_name2)
            self._remove_hashs(db1, db2)

            configdb = {"custom_link": "https://t.me/link/3", "auto_migrate": "False", "auto_migrate_log": "True", "auto_migrate_debug": "False"}
            self._db.set(db1, "__config__", configdb)

            self.lookup(db_name2).config["custom_link"] = "https://t.me/link/3"
            self.lookup(db_name2).config["auto_migrate_debug"] = "True"
            return True

        if number == 5:
            self._clear_dbs(db1)
            self._default_newdb(db2, db_name2)
            self._remove_hashs(db1, db2)

            configdb = {"custom_link": "https://t.me/link/2", "auto_migrate": "False", "auto_migrate_log": "True", "auto_migrate_debug": "True"}
            self._db.set(db1, "__config__", configdb)

            self.lookup(db_name2).config["custom_link"] = "https://t.me/link/2"
            self.lookup(db_name2).config["auto_migrate_debug"] = "True"
            return True

    def _remove_hashs(self, db1, db2):
        if "hashs" in self._db[db1].keys():
            self._db[db1].pop("hashs")
        if "hashs" in self._db[db2].keys():
            self._db[db2].pop("hashs")
            return True

    def _clear_dbs(self, db1):
        self._db[db1] = {}
        self._db[db1].clear()

    def _default_newdb(self, db2, db_name2):
        configdb2 = {"custom_link": "https://t.me/link/0", "auto_migrate": "False", "auto_migrate_log": "True", "auto_migrate_debug": "True",}

        self._db.set(db2, "__config__", configdb2)
        for key, value in configdb2.items():
            self.lookup(db_name2).config[key] = value
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
    # 🌐 https://www.gnu.org/licenses/agpl-3.0.html
    """

    strings = {
        "_log_doc_migrated_db": "Migrated {} database of {} -> {}:\n{}",
        "_log_doc_migrated_cfgv_val": "[Dynamic={}] Migrated default config value:\n{} -> {}",
        "_log_doc_no_dynamic_migration": "No module config found. Did not dynamic migrate:\n{{{}: {}}}",
        "_log_doc_migrated_db_not_found": "`{}` database not found. Did not migrate {} -> {}",
    }

    changes = {
        "migration1": {
            "classname": {
                "old": "MigratorMod",
                "new": "ApoAutoMigratorMod" 
            },
            "name": {
                "old": "MigratorMod", 
                "new": "Apo-AutoMigratior"
            },
            "config": {
                "custom_link": {
                    "old": "https://t.me/link/1", 
                    "new": "https://t.me/link/2",
                },
            },
        },
        "migration2": {
            "classname": {
            },
            "name": {
            },
            "config": {
                "custom_link": {
                    "old": "https://t.me/link/2", 
                    "new": "https://t.me/link/3",
                },
                "auto_migrate_debug": {
                    "old": "True", 
                    "new": "False",
                },
            },
        },
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
        log: bool = False, # type: ignore
        debug: bool = False, # type: ignore
    ):
        self._client = client
        self._db = db
        self._classname = classname
        self._name = name
        self._migrate_to = list(self.changes)[-1]
        self.modules = modules
        self.log = log
        self.debug = debug
        self.hashs = self._db.get(self._classname, "hashs", [])

    async def migrate(self, log: bool = False, debug: bool = False):
        self.log = log
        self.debug = debug
        logger.error(f"Log: {self.log} | Debug: {self.debug}")
        self.hashs = self._db.get(self._classname, "hashs", [])

        migrate = await self.check_new_migration()
        full_migrated = await self.full_migrated()
        if migrate:
            await self._logger(f"Open migrations: {migrate}", self.debug)
            if await self._migrator_func():
                await self._logger("Migration done.", self.debug)
                return True
        elif not full_migrated:
            await self.force_set_hashs()
            await self._logger(f"Open migrations: {migrate} | Forcehash done: {self.hashs}", self.debug)
            return False
        else:
            await self._logger(f"Open migrations: {migrate} | Skip migration.", self.debug)
            return False
        return False
        
    async def auto_migrate_handler(self, auto_migrate: bool = False):
        self.hashs = self._db.get(self._classname, "hashs", [])
        migrate = await self.check_new_migration()
        full_migrated = await self.full_migrated()
        if auto_migrate and migrate:
            await self._logger(f"Open migrations: {migrate} | auto_migrate: {auto_migrate}", self.debug)
            if await self._migrator_func():
                await self._logger("Migration done.", self.debug)
                return
        elif not auto_migrate and not full_migrated:
            await self.force_set_hashs()
            await self._logger(f"Open migrations: {migrate} | auto_migrate: {auto_migrate} | Forcehash done: {self.hashs}", self.debug)
            return
        else:
            await self._logger(f"Open migrations: {migrate} | auto_migrate: {auto_migrate} | Skip migrate_handler.", self.debug)
            return
        return

    async def force_set_hashs(self):
        await self._set_missing_hashs()
        return True

    async def check_new_migration(self):
        chash = hashlib.md5(self._migrate_to.encode('utf-8')).hexdigest()
        if not self.hashs:
            self.hashs = []
        return chash not in self.hashs

    async def full_migrated(self):
        full_migrated = True
        for migration in self.changes:
            chash = hashlib.md5(migration.encode('utf-8')).hexdigest()
            if chash not in self.hashs:
                full_migrated = False
        return full_migrated

    async def _migrator_func(self):
        for migration in self.changes:
            chash = hashlib.md5(migration.encode('utf-8')).hexdigest()
            if chash not in self.hashs:
                old_classname, new_classname, old_name, new_name = await self._get_names(migration)
                for category in self.changes[migration]:
                    await self._copy_config_init(migration, old_classname, new_classname, old_name, new_name, category)
                await self._set_hash(chash)
        return True

    async def _copy_config_init(self, migration, old_classname, new_classname, old_name, new_name, category):
        if category == "classname":
            if self._classname != old_classname and (old_classname in self._db.keys() and self._db[old_classname] and old_classname is not None):
                await self._logger(f"{migration} | {category} | old_value: {str(old_classname)} | new_value: {str(new_classname)}", self.debug)
                await self._copy_config(category, old_classname, new_classname, new_name)
            else:
                await self._logger(self.strings["_log_doc_migrated_db_not_found"].format(category, old_classname, new_classname))
        elif category == "name":
            await self._logger(f"{migration} | {category} | old_value: {str(old_name)} | new_value: {str(new_name)}", self.debug)
            if self._name != old_name and (old_name in self._db.keys() and self._db[old_name] and old_name is not None):
                await self._copy_config(category, old_name, new_name, new_classname)
            else:
                await self._logger(self.strings["_log_doc_migrated_db_not_found"].format(category, old_name, new_name))
        elif category == "config":
                await self._migrate_cfg_values(migration, category, new_name, new_classname)
        return

    async def _get_names(self, migration):
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
                        await self._logger(f"{migration} | {category} | ({{old_value: {str(old_value)}}} `==` {{new_value: {str(value)}}}) `and` {{key: {key}}} `==` {{cnfg_key: {cnfg_key}}}", self.debug)
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
            self._db[new_name].clear()
        self._db[new_name] = copy.deepcopy(self._db[old_name])
        self._db.pop(old_name)
        await self._logger(self.strings["_log_doc_migrated_db"].format(category, old_name, new_name, self._db[new_name]))
        if category == "classname":
            await self._make_dynamic_config(name, new_name)
        if category == "name":
            await self._make_dynamic_config(new_name, name)
        return

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
            chash = hashlib.md5(migration.encode('utf-8')).hexdigest()
            if chash not in self.hashs:
                await self._set_hash(chash)

    async def _logger(self, log_string, debug: bool = False):
        if debug or self.log:
            return logger.info(log_string)
        return logger.debug(log_string)
