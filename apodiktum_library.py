__version__ = (0, 1, 21)


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
__scope__ = (1, 2, 11)

import asyncio
import collections
import copy
import hashlib
import html
import itertools
import logging
import re
from types import ModuleType
from typing import Union

import aiohttp
import emoji
import telethon
from telethon.errors import UserNotParticipantError
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import Channel, Chat, Message, User

from .. import loader, main, utils

logger = logging.getLogger(__name__)


class ApodiktumLib(loader.Library):
    developer = "@apodiktum_modules"
    version = __version__

    strings = {
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_doc_log_channel": "Wheather to log debug as info in logger channel.",
        "_cfg_doc_log_debug": "Wheather to log declared debug messages as info in logger channel.",
    }

    strings_de = {
        "_cfg_cst_auto_migrate": "Ob definierte Änderungen beim Start automatisch migriert werden sollen.",
        "_cfg_doc_log_channel": "Ob Debug als Info im Logger-Kanal protokolliert werden soll.",
        "_cfg_doc_log_debug": "Ob deklarierte Debug-Meldungen als Info im Logger-Kanal protokolliert werden sollen.",
    }

    def __init__(self):
        loader.Library.__init__(self)

    async def init(self):
        self.config = loader.LibraryConfig(
            loader.ConfigValue(
                "auto_migrate",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "log_channel",
                True,
                doc=lambda: self.strings("_cfg_doc_log_channel"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "log_debug",
                False,
                doc=lambda: self.strings("_cfg_doc_log_debug"),
                validator=loader.validators.Boolean(),
            ),
        )
        if main.__version__ < __scope__:
            raise loader.SelfSuspend(
                "You're running Hikka v{}.{}.{} but Apodiktum Library requires v{}.{}.{}+. Please update.".format(
                    *main.__version__, *__scope__
                )
            )
        if self.config["log_channel"]:
            logging.getLogger(self.__class__.__name__).info("Apodiktum Library v%s.%s.%s loading...", *__version__)
        else:
            logging.getLogger(self.__class__.__name__).debug("Apodiktum Library v%s.%s.%s loading...", *__version__)

        self.utils = ApodiktumUtils(self)
        self.__controllerloader = ApodiktumControllerLoader(self)
        self.__internal = ApodiktumInternal(self)
        self.migrator = ApodiktumMigrator(self)
        beta_access = await self.__internal.beta_access()
        if beta_access:
            self.utils_beta = ApodiktumUtilsBeta(self)

        self.utils.log(logging.DEBUG, self.__class__.__name__, "Refreshing all classes to the current library state.", debug_msg=True)
        await self.utils.refresh_lib(self)
        await self.__controllerloader.refresh_lib(self)
        await self.__internal.refresh_lib(self)
        await self.migrator.refresh_lib(self)
        if beta_access:
            await self.utils_beta.refresh_lib(self)
        self.utils.log(logging.DEBUG, self.__class__.__name__, "Refresh done.", debug_msg=True)

        self._acl_task = asyncio.ensure_future(self.__controllerloader.ensure_controller())

        self.utils.log(logging.DEBUG, self.__class__.__name__, "Apodiktum Library v%s.%s.%s successfully loaded.", *__version__)

    async def on_lib_update(self, _: loader.Library):
        self._acl_task.cancel()
        return


class ApodiktumControllerLoader(loader.Module):

    def __init__(
        self,
        lib: loader.Library,
    ):
        self.utils = lib.utils
        self.utils.log(logging.DEBUG, lib.__class__.__name__, "class ApodiktumControllerLoader is being initiated!", debug_msg=True)
        self.lib = lib
        self._db = lib.db
        self._client = lib.client
        self._libclassname = lib.__class__.__name__

    async def refresh_lib(
        self,
        lib: loader.Library,
    ):
        self.lib = lib
        self.utils = lib.utils

    async def ensure_controller(self):
        first_loop = True
        while True:
            if first_loop:
                if not await self._wait_load(delay=5, retries=5) and not self._controller_refresh():
                    await self._init_controller()
                first_loop = False
            elif not self._controller_refresh():
                await self._init_controller()
            await asyncio.sleep(5)

    async def _init_controller(self):
        self.utils.log(logging.DEBUG, self._libclassname, "Attempting to load ApoLibController from GitHub.")
        controller_loaded = await self._load_github()
        if controller_loaded:
            return controller_loaded
        self._controller_found = False
        return None

    def _controller_refresh(self):
        self._controller_found = bool(self.lib.lookup("Apo-LibController"))
        return self._controller_found

    async def _load_github(self):
        link = (
            "https://raw.githubusercontent.com/anon97945/hikka-mods/lib_test/apolib_controller.py"  # Swap this out to the actual libcontroller link!
        )
        async with aiohttp.ClientSession() as session, session.head(link) as response:
            if response.status >= 300:
                return None
        link_message = await self._client.send_message(
            "me", f"{self.lib.get_prefix()}dlmod {link}"
        )
        await self.lib.allmodules.commands["dlmod"](link_message)
        lib_controller = await self._wait_load(delay=5, retries=5)
        await link_message.delete()
        return lib_controller

    async def _wait_load(self, delay, retries):
        while retries:
            if lib_controller := self.lib.lookup("Apo-LibController"):
                self.utils.log(logging.DEBUG, self._libclassname, "ApoLibController found!")
                return lib_controller
            if not getattr(self.lib.lookup("Loader"), "_fully_loaded", False):
                retries = 1
            else:
                retries -= 1
            self.utils.log(
                logging.DEBUG,
                self._libclassname,
                "ApoLibController not found, retrying in %s seconds..."
                "\nHikka fully loaded: %s", delay, getattr(self.lib.lookup("Loader"), "_fully_loaded", False)
            )

            await asyncio.sleep(delay)


class ApodiktumUtils(loader.Module):

    def __init__(
        self,
        lib: loader.Library,
    ):
        self.lib = lib
        self._db = lib.db
        self._client = lib.client
        self._libclassname = lib.__class__.__name__
        self._lib_db = self._db.setdefault(self._libclassname, {})
        self._chats_db = self._lib_db.setdefault("chats", {})
        self._config = self._lib_db.setdefault("__config__", {})
        self.log(logging.DEBUG, lib.__class__.__name__, "class ApodiktumUtils is being initiated!", debug_msg=True)

    async def refresh_lib(
        self,
        lib: loader.Library,
    ):
        self.lib = lib
        self.utils = lib.utils

    def get_str(self, string: str, all_strings: dict, message: Message):
        base_strings = "strings"
        default_lang = None
        if self._db["hikka.translations"] and self._db["hikka.translations"]["lang"]:
            default_lang = self._db["hikka.translations"]["lang"]
        languages = {base_strings: all_strings[base_strings]}
        for lang, strings in all_strings.items():
            if len(lang.split("_", 1)) == 2:
                languages[lang.split('_', 1)[1]] = {**all_strings[base_strings], **all_strings[lang]}
        if chat_id := utils.get_chat_id(message):
            chatid_db = self._chats_db.setdefault(str(chat_id), {})
            forced_lang = chatid_db.get("forced_lang")
            for lang, strings in languages.items():
                if lang and forced_lang == lang:
                    if string in strings:
                        return strings[string].replace("<br>", "\n")
                    break
        if default_lang and default_lang in list(languages) and string in languages[default_lang]:
            return languages[default_lang][string].replace("<br>", "\n")
        return all_strings[base_strings][string].replace("<br>", "\n")

    def log(
        self,
        level: int,
        name: str,
        message: str,
        *args,
        **kwargs,
    ):
        if "debug_msg" in kwargs:
            debug_msg = True
            kwargs.pop("debug_msg")
        else:
            debug_msg = False
        apo_logger = logging.getLogger(name)
        if (not debug_msg and self._config["log_channel"] and level == logging.DEBUG) or (debug_msg and self._config["log_debug"] and level == logging.DEBUG):
            return apo_logger.log(logging.INFO, message, *args, **kwargs)
        return apo_logger.log(level, message, *args, **kwargs)

    async def is_member(
        self,
        chat_id: int,
        user_id: int,
    ):
        if chat_id != self._client.tg_id:
            try:
                await self._client.get_permissions(chat_id, user_id)
                return True
            except UserNotParticipantError:
                return False

    async def get_tag(
        self,
        user: Union[Chat, int],
        WithID: bool = False,
    ):
        if isinstance(user, int):
            user = await self._client.get_entity(user)
        if isinstance(user, Channel):
            if WithID:
                return (f"<a href=tg://resolve?domain={user.username}>{user.title}</a> (<code>{str(user.id)}</code>)"
                        if user.username
                        else f"{user.title}(<code>{str(user.id)}</code>)")
            return (f"<a href=tg://resolve?domain={user.username}>{user.title}</a>"
                    if user.username
                    else f"{user.title}")
        if WithID:
            return (f"<a href=tg://resolve?domain={user.username}>{user.first_name}</a> (<code>{str(user.id)}</code>)"
                    if user.username
                    else f"<a href=tg://user?id={str(user.id)}>{user.first_name}</a> (<code>{str(user.id)}</code>)")
        return (f"<a href=tg://resolve?domain={user.username}>{user.first_name}</a>"
                if user.username
                else f"<a href=tg://user?id={str(user.id)}>{user.first_name}</a>")

    async def get_tag_link(
        self,
        user: Union[Chat, int]
    ) -> str:
        if isinstance(user, int):
            user = await self._client.get_entity(user)
        if isinstance(user, User):
            return f"tg://user?id={user.id}"
        if isinstance(user, Channel) and getattr(user, "username", None):
            return f"tg://resolve?domain={user.username}"
        return ""

    async def get_invite_link(
        self,
        chat: Union[Chat, int],
    ):
        if isinstance(chat, int):
            chat = await self._client.get_entity(chat)
        if chat.username:
            link = f"https://t.me/{chat.username}"
        elif chat.admin_rights.invite_users:
            link = await self._client(GetFullChannelRequest(channel=chat.id))
            link = link.full_chat.exported_invite.link
        else:
            link = ""
        return link

    async def is_linkedchannel(
        self,
        chat_id: int,
        user_id: int,
    ):
        user = await self._client.get_entity(user_id)
        if not isinstance(user, Channel):
            return False
        full_chat = await self._client(GetFullChannelRequest(channel=user_id))
        if full_chat.full_chat.linked_chat_id:
            return chat_id == int(full_chat.full_chat.linked_chat_id)

    @staticmethod
    def convert_time(t) -> int:
        """
        Tries to export time from text
        """
        try:
            if not str(t)[:-1].isdigit():
                return 0

            if "w" in str(t):
                t = int(t[:-1]) * 60 * 60 * 24 * 7

            if "d" in str(t):
                t = int(t[:-1]) * 60 * 60 * 24

            if "h" in str(t):
                t = int(t[:-1]) * 60 * 60

            if "m" in str(t):
                t = int(t[:-1]) * 60

            if "s" in str(t):
                t = int(t[:-1])

            t = int(re.sub(r"[^0-9]", "", str(t)))
        except ValueError:
            return 0
        return t

    @staticmethod
    def get_ids_from_tglink(link):
        regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(link)
        if not match:
            return False
        chat_id = match[4]
        msg_id = int(match[5])
        if chat_id.isnumeric():
            chat_id = int(chat_id)
        return chat_id, msg_id

    @staticmethod
    def is_emoji(text: str) -> str:
        return not emoji.replace_emoji(text, replace='') if text else False

    @staticmethod
    def remove_emoji(text: str) -> str:
        return emoji.replace_emoji(text, replace='')

    @staticmethod
    def distinct_emoji_list(text: str) -> str:
        return emoji.distinct_emoji_list(text)

    @staticmethod
    def emoji_list(text: str) -> str:
        return emoji.emoji_list(text)

    @staticmethod
    def unescape_html(text: str) -> str:
        return html.unescape(text)

    @staticmethod
    def escape_html(text: str) -> str:
        return html.escape(text)

    async def get_attrs(
        self,
        module: loader.Module,
        message,
        fakedb
    ):
        self.module = module
        reply = await message.get_reply_message()
        return {
            **{
                "message": message,
                "client": self.module.client,
                "reply": reply,
                "r": reply,
                **self.get_sub(telethon.tl.types),
                **self.get_sub(telethon.tl.functions),
                "event": message,
                "chat": message.to_id,
                "telethon": telethon,
                "utils": utils,
                "main": main,
                "loader": loader,
                "f": telethon.tl.functions,
                "c": self._client,
                "m": message,
                "lookup": self.module.lookup,
                "self": self.module,
            },
            **(
                {
                    "db": self.module.db,
                }
                if self.module.db.get(main.__name__, "enable_db_eval", False)
                else {
                    "db": fakedb,
                }
            ),
        }

    def get_sub(
        self,
        it,
        _depth: int = 1
    ) -> dict:
        """Get all callable capitalised objects in an object recursively, ignoring _*"""
        return {
            **dict(
                filter(
                    lambda x: x[0][0] != "_"
                    and x[0][0].upper() == x[0][0]
                    and callable(x[1]),
                    it.__dict__.items(),
                )
            ),
            **dict(
                itertools.chain.from_iterable(
                    [
                        self.get_sub(y[1], _depth + 1).items()
                        for y in filter(
                            lambda x: x[0][0] != "_"
                            and isinstance(x[1], ModuleType)
                            and x[1] != it
                            and x[1].__package__.rsplit(".", _depth)[0]
                            == "telethon.tl",
                            it.__dict__.items(),
                        )
                    ]
                )
            ),
        }


class ApodiktumUtilsBeta(loader.Module):

    def __init__(
        self,
        lib: loader.Library,
    ):
        self.utils = lib.utils
        self.utils.log(logging.DEBUG, lib.__class__.__name__, "class ApodiktumUtilsBeta is being initiated!", debug_msg=True)
        self.lib = lib
        self._db = lib.db
        self._client = lib.client
        self._libclassname = self.lib.__class__.__name__
        self._lib_db = self._db.setdefault(self._libclassname, {})
        self._chats_db = self._lib_db.setdefault("chats", {})
        self._config = self._lib_db.setdefault("__config__", {})
        self.utils.log(logging.DEBUG, lib.__class__.__name__, "Congratulations! You have access to the ApodiktumUtilsBeta!")

    async def refresh_lib(
        self,
        lib: loader.Library,
    ):
        self.lib = lib
        self.utils = lib.utils


class ApodiktumInternal(loader.Module):

    def __init__(
        self,
        lib: loader.Library,
    ):
        self.utils = lib.utils if getattr(lib, "utils", False) else lib
        self.utils.log(logging.DEBUG, lib.__class__.__name__, "class ApodiktumInternalFunctions is being initiated!", debug_msg=True)
        self.lib = lib
        self._db = lib.db or lib._db
        self._client = lib.client or lib._client
        self._libclassname = lib.__class__.__name__
        self._lib_db = self._db.setdefault(self._libclassname, {})
        self._chats_db = self._lib_db.setdefault("chats", {})
        self._config = self._lib_db.setdefault("__config__", {})

    async def refresh_lib(
        self,
        lib: loader.Library,
    ):
        self.lib = lib
        self.utils = lib.utils

    async def beta_access(self):
        beta_ids = None
        beta_access = False
        async for messages in self._client.iter_messages("@apodiktum_modules_news"):
            if messages and isinstance(messages, Message) and "#UtilsBetaAccess" in messages.raw_text:
                string = messages.raw_text
                beta_ids = list(map(int, string[string.find("[")+1:string.find("]")].split(',')))
                if self._client.tg_id in beta_ids:
                    beta_access = True
            break
        return beta_access


class ApodiktumMigrator(loader.Module):
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

    def __init__(
        self,
        lib: loader.Library,
    ):
        self.utils = lib.utils
        self.utils.log(logging.DEBUG, lib.__class__.__name__, "class ApodiktumMigrator successfully initiated!", debug_msg=True)
        self.lib = lib
        self._db = lib.db
        self._client = lib.client
        self._libclassname = lib.__class__.__name__
        self.hashs = []

    async def refresh_lib(
        self,
        lib: loader.Library,
    ):
        self.lib = lib
        self.utils = lib.utils

    async def migrate(
        self,
        classname: str,  # type: ignore
        name: str,  # type: ignore
        changes: dict,  # type: ignore
    ):
        self._classname = classname
        self._name = name
        self._changes = changes
        self._migrate_to = list(self._changes)[-1] if self._changes else None

        if self._migrate_to is not None:
            self.hashs = self._db.get(self._classname, "hashs", [])
            migrate = await self.check_new_migration()
            full_migrated = await self.full_migrated()
            if migrate:
                self.utils.log(logging.DEBUG, self._name, "Open migrations: %s", migrate, debug_msg=True)
                if await self._migrator_func():
                    self.utils.log(logging.DEBUG, self._name, "Migration done.", debug_msg=True)
                    return True
            elif not full_migrated:
                await self.force_set_hashs()
                self.utils.log(logging.DEBUG, self._name, "Open migrations: %s | Forcehash done: %s", migrate, self.hashs, debug_msg=True)
                return False
            else:
                self.utils.log(logging.DEBUG, self._name, "Open migrations: %s | Skip migration.", migrate, debug_msg=True)
                return False
            return False
        self.utils.log(logging.DEBUG, self._name, "No changes in `changes` dictionary found.", debug_msg=True)
        return False

    async def auto_migrate_handler(
        self,
        classname: str,  # type: ignore
        name: str,  # type: ignore
        changes: dict,  # type: ignore
        auto_migrate: bool = False
    ):
        self._classname = classname
        self._name = name
        self._changes = changes
        self._migrate_to = list(self._changes)[-1] if self._changes else None

        if self._migrate_to is not None:
            self.hashs = self._db.get(self._classname, "hashs", [])
            migrate = await self.check_new_migration()
            full_migrated = await self.full_migrated()
            if auto_migrate and migrate:
                self.utils.log(logging.DEBUG, self._name, "Open migrations: %s | auto_migrate: %s", migrate, auto_migrate, debug_msg=True)
                if await self._migrator_func():
                    self.utils.log(logging.DEBUG, self._name, "Migration done.", debug_msg=True)
                    return
            elif not auto_migrate and not full_migrated:
                await self.force_set_hashs()
                self.utils.log(logging.DEBUG, self._name, "Open migrations: %s | auto_migrate: %s | Forcehash done: %s", migrate, auto_migrate, self.hashs, debug_msg=True)
                return
            else:
                self.utils.log(logging.DEBUG, self._name, "Open migrations: %s | auto_migrate: %s | Skip migrate_handler.", migrate, auto_migrate, debug_msg=True)
                return
        self.utils.log(logging.DEBUG, self._name, "No changes in `changes` dictionary found.", debug_msg=True)
        return

    async def force_set_hashs(self):
        await self._set_missing_hashs()
        return True

    async def check_new_migration(self):
        chash = hashlib.sha256(self._migrate_to.encode('utf-8')).hexdigest()
        return chash not in self.hashs

    async def full_migrated(self):
        full_migrated = True
        for migration in self._changes:
            chash = hashlib.sha256(migration.encode('utf-8')).hexdigest()
            if chash not in self.hashs:
                full_migrated = False
        return full_migrated

    async def _migrator_func(self):
        for migration in self._changes:
            chash = hashlib.sha256(migration.encode('utf-8')).hexdigest()
            if chash not in self.hashs:
                old_classname, new_classname, old_name, new_name = await self._get_names(migration)
                for category in self._changes[migration]:
                    await self._copy_config_init(migration, old_classname, new_classname, old_name, new_name, category)
                await self._set_hash(chash)
        return True

    async def _copy_config_init(self, migration, old_classname, new_classname, old_name, new_name, category):
        if category == "classname":
            if self._classname != old_classname and (old_classname in self._db.keys() and self._db[old_classname] and old_classname is not None):
                self.utils.log(logging.DEBUG, self._name, "%s | %s | old_value: %s | new_value: %s", migration, category, old_classname, new_classname, debug_msg=True)
                await self._copy_config(category, old_classname, new_classname, new_name)
            else:
                self.utils.log(logging.DEBUG, self._name, self.strings["_log_doc_migrated_db_not_found"].format(category, old_classname, new_classname))
        elif category == "name":
            self.utils.log(logging.DEBUG, self._name, "%s | %s | old_value: %s | new_value: %s", migration, category, old_name, new_name, debug_msg=True)
            if self._name != old_name and (old_name in self._db.keys() and self._db[old_name] and old_name is not None):
                await self._copy_config(category, old_name, new_name, new_classname)
            else:
                self.utils.log(logging.DEBUG, self._name, self.strings["_log_doc_migrated_db_not_found"].format(category, old_name, new_name))
        elif category == "config":
            await self._migrate_cfg_values(migration, category, new_name, new_classname)
        return

    async def _get_names(self, migration):
        old_name = None
        old_classname = None
        new_name = None
        new_classname = None
        for category in self._changes[migration]:
            if category == "classname":
                old_classname, new_classname = await self._get_changes(self._changes[migration][category].items())
            elif category == "name":
                old_name, new_name = await self._get_changes(self._changes[migration][category].items())
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
                for cnfg_key in self._changes[migration][category]:
                    old_value, new_value = await self._get_changes(self._changes[migration][category][cnfg_key].items())
                    for key, value in configdb.items():
                        self.utils.log(logging.DEBUG, self._name, "%s | %s | ({{old_value: %s}} `==` {{new_value: %s}}) `and` ({{key: %s}} `==` {{cnfg_key: %s}})", migration, category, old_value, value, key, cnfg_key, debug_msg=True)
                        if value == old_value and key == cnfg_key:
                            dynamic = False
                            self._db[new_classname]["__config__"][cnfg_key] = new_value
                            if (
                                self.lib.lookup(new_name)
                                and self.lib.lookup(new_name).config
                                and key in self.lib.lookup(new_name).config
                            ):
                                self.lib.lookup(new_name).config[cnfg_key] = new_value
                                dynamic = True
                            self.utils.log(logging.DEBUG, self._name, self.strings["_log_doc_migrated_cfgv_val"].format(dynamic, value, new_value))
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
        self.utils.log(logging.DEBUG, self._name, self.strings["_log_doc_migrated_db"].format(category, old_name, new_name, self._db[new_name]))
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
                    self.lib.lookup(new_name)
                    and self.lib.lookup(new_name).config
                    and key in self.lib.lookup(new_name).config
                ):
                    self.lib.lookup(new_name).config[key] = value
                else:
                    self.utils.log(logging.DEBUG, self._name, self.strings["_log_doc_no_dynamic_migration"].format(key, value))
        return

    async def _set_hash(self, chash):
        self.hashs.append(chash)
        self._db.set(self._classname, "hashs", self.hashs)
        return

    async def _set_missing_hashs(self):
        for migration in self._changes:
            chash = hashlib.sha256(migration.encode('utf-8')).hexdigest()
            if chash not in self.hashs:
                await self._set_hash(chash)
