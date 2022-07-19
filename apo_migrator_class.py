__version__ = (0, 0, 12)


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
# scope: hikka_min 1.2.11

import logging

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

    strings_en = {
    }

    strings_de = {
    }

    strings_ru = {
    }

    db_classnames = {
        "db1": "MigratorMod",
        "db2": "ApoAutoMigratorMod",
    }

    db_names = {
        "db1": "Migrator",
        "db2": "Apo-AutoMigratior",
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "custom_link",
                "https://t.me/link/0",
                validator=loader.validators.Link(),
            ),  # for test commands
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

    all_strings = {
        "strings": strings,
        "strings_en": strings,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    changes = {
        "migration1": {
            "classname": {
                "old": "MigratorMod",
                "new": "ApoAutoMigratorMod",
            },
            "name": {
                "old": "Migrator",
                "new": "Apo-AutoMigratior",
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

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.apo_lib = await self.import_lib(
            "https://raw.githubusercontent.com/anon97945/hikka-mods/master/apodiktum_library.py",
            suspend_on_error=True,
        )
        await self.apo_lib.migrator.auto_migrate_handler(self.__class__.__name__, self.strings("name"), self.changes, self.lookup("ApodiktumLib").config["auto_migrate"])

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
        if await self.apo_lib.migrator.migrate(self.__class__.__name__, self.strings("name"), self.changes):
            await utils.answer(message, "Migrated.")
        else:
            await utils.answer(message, "Not migrated!")

    async def resetcmd(self, message: Message):
        """
        <int|1-5>
        This will reset the module.
        """
        args = utils.get_args_raw(message)
        if await self._reset(int(args), self.db_classname[0], self.db_classname[1], self.db_name[0], self.db_name[1]):
            await utils.answer(message, f"Reset done.\nOld ClassDB ({self.db_classname[0]}): {self._db[self.db_classname[0]]}\n\nNew ClassDB ({self.db_classname[1]}): {self._db[self.db_classname[1]]}\n\nOld NameDB ({self.db_name[0]}): {self._db[self.db_name[0]]}\n\nNew NameDB ({self.db_name[1]}): {self._db[self.db_name[1]]}")
        else:
            await utils.answer(message, "no reset")

    async def getdbcmd(self, message: Message):
        """
        This will reset the module.
        """
        if self.db_classname[0] in self._db.keys():
            await utils.answer(message, f"\nOld ClassDB ({self.db_classname[0]}): {self._db[self.db_classname[0]]}\n\nNew ClassDB ({self.db_classname[1]}): {self._db[self.db_classname[1]]}\nOld NameDB ({self.db_name[0]}): {self._db[self.db_name[0]]}\n\nNew NameDB ({self.db_name[1]}): {self._db[self.db_name[1]]}")
        else:
            await utils.answer(message, f"\nOld ClassDB ({self.db_classname[0]}): `None/Deleted`\n\nNew ClassDB ({self.db_classname[1]}): {self._db[self.db_classname[1]]}\n\nOld NameDB ({self.db_name[0]}): `None/Deleted`\nNew NameDB ({self.db_name[1]}): {self._db[self.db_name[1]]}")

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

    async def _reset(self, number: int, db1, db2, db_name1, db_name2):
        if number == 1:
            self._clear_dbs(db1, db_name1, db_name2)
            self._default_newdb(db2, db_name1, db_name2)
            self._remove_hashs(db1, db2)

            confignamedb = {"some_name": "some_value"}
            self._db.set(db_name1, "__config__", confignamedb)
            db_name1 = self._db.get(db_name1, "hello", {})
            db_name1.setdefault("hello", "world")

            configdb = {"custom_link": "https://t.me/link/1", "auto_migrate": "False", "auto_migrate_log": "True", "auto_migrate_debug": "True"}
            self._db.set(db1, "__config__", configdb)
            return True

        if number == 2:
            self._clear_dbs(db1, db_name1, db_name2)
            self._default_newdb(db2, db_name1, db_name2)
            self._remove_hashs(db1, db2)

            confignamedb = {"some_name": "some_value"}
            self._db.set(db_name1, "__config__", confignamedb)
            db_name1 = self._db.get(db_name1, "hello", {})
            db_name1.setdefault("hello", "world")

            configdb = {"custom_link": "https://t.me/link/5", "auto_migrate": "False", "auto_migrate_log": "True", "auto_migrate_debug": "True"}
            self._db.set(db1, "__config__", configdb)
            return True

        if number == 3:
            self._clear_dbs(db1, db_name1, db_name2)
            self._default_newdb(db2, db_name1, db_name2)
            self._remove_hashs(db1, db2)

            configdb = {"custom_link": "https://t.me/link/2", "auto_migrate": "False", "auto_migrate_log": "True", "auto_migrate_debug": "True"}
            self._db.set(db2, "__config__", configdb)

            confignamedb = {"some_name": "some_value"}
            self._db.set(db_name1, "__config__", confignamedb)
            db_name1 = self._db.get(db_name1, "hello", {})
            db_name1.setdefault("hello", "world")

            self.lookup(db_name2).config["custom_link"] = "https://t.me/link/2"
            return True

        if number == 4:
            self._clear_dbs(db1, db_name1, db_name2)
            self._default_newdb(db2, db_name1, db_name2)
            self._remove_hashs(db1, db2)

            configdb = {"custom_link": "https://t.me/link/3", "auto_migrate": "False", "auto_migrate_log": "True", "auto_migrate_debug": "False"}
            self._db.set(db1, "__config__", configdb)

            confignamedb = {"some_name": "some_value"}
            self._db.set(db_name1, "__config__", confignamedb)
            db_name1 = self._db.get(db_name1, "hello", {})
            db_name1.setdefault("hello", "world")

            self.lookup(db_name2).config["custom_link"] = "https://t.me/link/3"
            self.lookup(db_name2).config["auto_migrate_debug"] = "True"
            return True

        if number == 5:
            self._clear_dbs(db1, db_name1, db_name2)
            self._default_newdb(db2, db_name1, db_name2)
            self._remove_hashs(db1, db2)

            configdb = {"custom_link": "https://t.me/link/2", "auto_migrate": "False", "auto_migrate_log": "True", "auto_migrate_debug": "True"}
            self._db.set(db1, "__config__", configdb)

            confignamedb = {"some_name": "some_value"}
            self._db.set(db_name1, "__config__", confignamedb)
            db_name1 = self._db.get(db_name1, "hello", {})
            db_name1.setdefault("hello", "world")

            self.lookup(db_name2).config["custom_link"] = "https://t.me/link/2"
            self.lookup(db_name2).config["auto_migrate_debug"] = "True"
            return True

    def _remove_hashs(self, db1, db2):
        if "hashs" in self._db[db1].keys():
            self._db[db1].pop("hashs")
        if "hashs" in self._db[db2].keys():
            self._db[db2].pop("hashs")
        return True

    def _clear_dbs(self, db1, db_name1, db_name2):
        self._db[db1] = {}
        self._db[db1].clear()
        self._db[db_name1] = {}
        self._db[db_name1].clear()
        self._db[db_name2] = {}

    def _default_newdb(self, db2, db_name1, db_name2):
        configdb2 = {"custom_link": "https://t.me/link/0", "auto_migrate": "False", "auto_migrate_log": "True", "auto_migrate_debug": "True"}

        self._db.set(db2, "__config__", configdb2)
        for key, value in configdb2.items():
            self.lookup(db_name2).config[key] = value
        self._db[db_name1].setdefault("1234", "5678")
