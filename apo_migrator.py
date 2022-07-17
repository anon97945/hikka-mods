__version__ = (0, 1, 6)


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

import collections  # for MigratorClass
import hashlib  # for MigratorClass
import copy     # for MigratorClass

from .. import loader, utils
from telethon.tl.types import Message
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)

ClassNames = {
    "AutoUpdateMod": "ApodiktumAutoUpdateMod",
    "PMLogMod": "ApodiktumPMLogMod",
    "ShowViewsMod": "ApodiktumShowViewsMod",
    "TTSMod": "ApodiktumTTSMod",
    "anoninfoMod": "ApodiktumInfoMod",
    "gtranslateMod": "ApodiktumGTranslateMod",
    "herokumanagerMod": "ApodiktumHerokuManagerMod",
    "voicetoolsMod": "ApodiktumVoiceToolsMod",
}

ModuleNames = {
    "AnonInfo": "Apo Info",
    "Apodiktum Admin Tools": "Apo AdminTools",
    "Apodiktum AutoReact": "Apo AutoReact",
    "Apodiktum DND": "Apo DND",
    "Apodiktum Purge": "Apo Purge",
    "Google Translator": "Apo GoogleTranslator",
    "Heroku Manager": "Apo HerokuManager",
    "HikkaAutoUpdater": "Apo AutoUpdater",
    "Login Code Reciever": "Apo LoginCodeReciever",
    "PM Logger": "Apo PMLogger",
    "PyPNG": "Apo PyPNG",
    "Save Message": "Apo SaveMessage",
    "ShowViews": "Apo ShowViews",
    "Text To Speech": "Apo TextToSpeech",
    "VoiceTools": "Apo VoiceTools",
}

Links = {
    "https://github.com/anon97945/hikka-mods/raw/master/anoninfo.py": "https://github.com/anon97945/hikka-mods/raw/master/apoinfo.py",
    "https://github.com/anon97945/hikka-mods/raw/master/apodiktumadmintools.py": "https://github.com/anon97945/hikka-mods/raw/master/admintools.py",
}


@loader.tds
class ApodiktumMigratorMod(loader.Module):
    """
    Migrate old names with new ones.
    """
    strings = {
        "name": "Apo Migrator",
        "developer": "@anon97945",
        "_btn_close": "🚫 Close",
        "_btn_force": "Force migrate",
        "_btn_no": "🚫 No",
        "_btn_restart": "🔄 Restart",
        "_btn_yes": "✅ Yes",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_cst_auto_migrate_debug": "Wheather log debug messages of auto migrate.",
        "_cfg_cst_auto_migrate_log": "Wheather log auto migrate as info(True) or debug(False).",
        "_log_doc_migrated_db": "Migrated {} of {} -> {}:\n{}.",
        "_log_doc_migrated_finish": "Migrated all modules.",
        "_log_doc_migrates": "Migrated {}:\n{} -> {}.",
        "_log_doc_migrating": "Migrating modules...",
        "already_migrated": "<b>[Error] You already migrated your modules.</b>",
        "migrate_now": "<b>Hello👋🏻,\ndo you want to migrate now?\nEnsure to backup your DB before!</b>\n<code>.backupdb</code>",
        "restart_now": "<b><u>Done.</u>\nDo you want to restart now?</b>",
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
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
        self.base_strings = self.strings._base_strings
        # MigratorClass
        self._migrator = MigratorClass()  # MigratorClass define
        await self._migrator.init(client, db, self, self.__class__.__name__, self.strings("name"), self.config["auto_migrate_log"], self.config["auto_migrate_debug"])  # MigratorClass Initiate
        await self._migrator.auto_migrate_handler(self.config["auto_migrate"])
        # MigratorClass

    def _strings(self, string: str, chat_id: int = None):
        if self.lookup("Apo-Translations") and chat_id:
            forced_translation_db = self.lookup("Apo-Translations").config
            strings_en = self.strings_en if getattr(self, "strings_en", False) else {}
            strings_de = self.strings_de if getattr(self, "strings_de", False) else {}
            strings_ru = self.strings_ru if getattr(self, "strings_ru", False) else {}
            languages = {
                "en_chats": {**self.base_strings, **strings_en},
                "de_chats": {**self.base_strings, **strings_de},
                "ru_chats": {**self.base_strings, **strings_ru},
            }
            for lang, strings in languages.items():
                if chat_id in forced_translation_db[lang]:
                    if string in strings:
                        return strings[string]
                    logger.debug(f"String: {string} not found in\n{strings}")
                    break
        return self.strings(string)

    async def apomigratecmd(self, message: Message):
        """
        This will migrate all your old modules to new ones, including Config.
        """
        chat_id = utils.get_chat_id(message)

        if self.get("hash") == "e1cc9d13bf96ec1aca7edd2fb67f0816":
            await self.inline.form(message=message,
                                   text=self._strings("already_migrated", utils.get_chat_id(message)),
                                   reply_markup=[
                                                    {
                                                        "text": self._strings("_btn_force", utils.get_chat_id(message)),
                                                        "callback": self._migrate,
                                                        "args": (chat_id,),
                                                    },
                                                    {
                                                        "text": self._strings("_btn_close", utils.get_chat_id(message)),
                                                        "callback": self._close
                                                    }
                                                ])
            return
        await self.inline.form(message=message,
                               text=self._strings("migrate_now", utils.get_chat_id(message)),
                               reply_markup=[
                                                {
                                                    "text": self._strings("_btn_yes", utils.get_chat_id(message)),
                                                    "callback": self._migrate,
                                                    "args": (chat_id,),
                                                },
                                                {
                                                    "text": self._strings("_btn_no", utils.get_chat_id(message)),
                                                    "callback": self._close,
                                                },
                                                ])

    async def _migrate(self, call: InlineCall, chat_id):
        logger.info(self.strings("_log_doc_migrating"))
        await self._migrate_db()
        logger.info(self.strings("_log_doc_migrated_finish"))
        self.set("hash", "e1cc9d13bf96ec1aca7edd2fb67f0816")
        await call.edit(text=self.strings("restart_now"),
                        reply_markup={"text": self.strings("_btn_restart"),
                                      "callback": self._restart,
                                      "args": (chat_id,)
                                      })

    async def _migrate_db(self):
        old_db = self._db.get("Loader", "loaded_modules")
        new_db = await self._key_rename(old_db, ClassNames)
        new_db = await self._update_key_value(new_db, Links)
        self._db.set("Loader", "loaded_modules", new_db)
        await self._copy_config(ClassNames, "ClassConfig")
        await self._copy_config(ModuleNames, "ModuleConfig")

    async def _restart(self, call: InlineCall, chat_id):
        await call.delete()
        await self.allmodules.commands["update"](
            await self._client.send_message(chat_id, f"{self.get_prefix()}restart --force")
        )

    async def _close(self, call) -> None:
        await call.delete()

    async def _copy_config(self, mlist, typename):
        for old_name, new_name in mlist.items():
            if old_name in self._db.keys():
                old_config = self._db[old_name]
                for key, _value in old_config.items():
                    self._db.set(new_name, key, self._db.get(old_name, key))
                    logger.info(self.strings("_log_doc_migrated_db").format(typename, old_name, new_name, self._db.get(old_name, key)))

    async def _key_rename(self, old_db, mlist):
        new_dict = {}
        for key, _value in zip(old_db.keys(), old_db.values()):
            new_key = mlist.get(key, key)
            new_dict[new_key] = old_db[key]
        for old_key, new_key in mlist.items():
            if new_key in new_dict:
                logger.info(self.strings("_log_doc_migrates").format("old ClassName", old_key, new_key))
        return new_dict

    async def _update_key_value(self, new_db, mlist):
        for old_value, new_value in mlist.items():
            for key, value in new_db.items():
                if value == old_value:
                    new_db[key] = new_value
                    logger.info(self.strings("_log_doc_migrates").format("old URL", old_value, new_value))
        return new_db


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
