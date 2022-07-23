__version__ = (0, 1, 13)


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
# meta banner: https://i.ibb.co/N7c0Ks2/cat.jpg
# meta pic: https://i.ibb.co/4jLTywZ/apo-modules.jpg

# scope: hikka_only
# scope: hikka_min 1.2.11

import logging

from telethon.tl.types import Message

from .. import loader, utils
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
    "https://github.com/anon97945/hikka-mods/raw/master/anoninfo.py": (
        "https://github.com/anon97945/hikka-mods/raw/master/apoinfo.py"
    ),
    "https://github.com/anon97945/hikka-mods/raw/master/apodiktumadmintools.py": (
        "https://github.com/anon97945/hikka-mods/raw/master/admintools.py"
    ),
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
        "_log_doc_migrated_db": "Migrated {} of {} -> {}:\n{}.",
        "_log_doc_migrated_finish": "Migrated all modules.",
        "_log_doc_migrates": "Migrated {}:\n{} -> {}.",
        "_log_doc_migrating": "Migrating modules...",
        "already_migrated": "<b>[Error] You already migrated your modules.</b>",
        "migrate_now": (
            "<b>Hello👋🏻,\ndo you want to migrate now?\nEnsure to backup your DB"
            " before!</b>\n<code>.backupdb</code>"
        ),
        "restart_now": "<b><u>Done.</u>\nDo you want to restart now?</b>",
    }

    strings_en = {}

    strings_de = {}

    strings_ru = {}

    all_strings = {
        "strings": strings,
        "strings_en": strings,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
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
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.apo_lib = await self.import_lib(
            "https://raw.githubusercontent.com/anon97945/hikka-mods/lib_test/apodiktum_library.py",
            suspend_on_error=True,
        )
        self.apo_lib.apodiktum_module()

    async def apomigratecmd(self, message: Message):
        """
        This will migrate all your old modules to new ones, including Config.
        """
        chat_id = utils.get_chat_id(message)

        if self.get("hash") == "e1cc9d13bf96ec1aca7edd2fb67f0816":
            await self.inline.form(
                message=message,
                text=self.apo_lib.utils.get_str(
                    "already_migrated", self.all_strings, message
                ),
                reply_markup=[
                    {
                        "text": self.apo_lib.utils.get_str(
                            "_btn_force", self.all_strings, message
                        ),
                        "callback": self._migrate,
                        "args": (chat_id,),
                    },
                    {
                        "text": self.apo_lib.utils.get_str(
                            "_btn_close", self.all_strings, message
                        ),
                        "callback": self._close,
                    },
                ],
            )
            return
        await self.inline.form(
            message=message,
            text=self.apo_lib.utils.get_str("migrate_now", self.all_strings, message),
            reply_markup=[
                {
                    "text": self.apo_lib.utils.get_str(
                        "_btn_yes", self.all_strings, message
                    ),
                    "callback": self._migrate,
                    "args": (chat_id,),
                },
                {
                    "text": self.apo_lib.utils.get_str(
                        "_btn_no", self.all_strings, message
                    ),
                    "callback": self._close,
                },
            ],
        )

    async def _migrate(self, call: InlineCall, chat_id):
        logger.info(self.strings("_log_doc_migrating"))
        await self._migrate_db()
        logger.info(self.strings("_log_doc_migrated_finish"))
        self.set("hash", "e1cc9d13bf96ec1aca7edd2fb67f0816")
        await call.edit(
            text=self.strings("restart_now"),
            reply_markup={
                "text": self.strings("_btn_restart"),
                "callback": self._restart,
                "args": (chat_id,),
            },
        )

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
            await self._client.send_message(
                chat_id, f"{self.get_prefix()}restart --force"
            )
        )

    async def _close(self, call) -> None:
        await call.delete()

    async def _copy_config(self, mlist, typename):
        for old_name, new_name in mlist.items():
            if old_name in self._db.keys():
                old_config = self._db[old_name]
                for key, _value in old_config.items():
                    self._db.set(new_name, key, self._db.get(old_name, key))
                    logger.info(
                        self.strings("_log_doc_migrated_db").format(
                            typename, old_name, new_name, self._db.get(old_name, key)
                        )
                    )

    async def _key_rename(self, old_db, mlist):
        new_dict = {}
        for key, _value in zip(old_db.keys(), old_db.values()):
            new_key = mlist.get(key, key)
            new_dict[new_key] = old_db[key]
        for old_key, new_key in mlist.items():
            if new_key in new_dict:
                logger.info(
                    self.strings("_log_doc_migrates").format(
                        "old ClassName", old_key, new_key
                    )
                )
        return new_dict

    async def _update_key_value(self, new_db, mlist):
        for old_value, new_value in mlist.items():
            for key, value in new_db.items():
                if value == old_value:
                    new_db[key] = new_value
                    logger.info(
                        self.strings("_log_doc_migrates").format(
                            "old URL", old_value, new_value
                        )
                    )
        return new_db
