__version__ = (0, 1, 41)


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
__hikka_min__ = (1, 2, 11)

import asyncio
import collections
import contextlib
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
import requests
import telethon
from telethon.errors import UserNotParticipantError
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import Channel, Chat, Message, MessageEntityUrl, User

from .. import loader, main, utils

logger = logging.getLogger(__name__)


class ApodiktumLib(loader.Library):
    """
    The Apodiktum Library is a collection of useful functions and classes for all Hikka developers.
    """
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
        if main.__version__ < __hikka_min__:
            hikka_min_error = (
                f"You're running Hikka v{main.__version__[0]}.{main.__version__[1]}.{main.__version__[2]} "
                f"but Apodiktum Library v{__version__[0]}.{__version__[1]}.{__version__[2]} requires "
                f"Hikka v{__hikka_min__[0]}.{__hikka_min__[1]}.{__hikka_min__[2]}+. Please update."
            )
            logging.getLogger(self.__class__.__name__).debug(hikka_min_error)
            raise loader.SelfSuspend(hikka_min_error)

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
        self.__internal.send_stats()

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
    """
    This class is used to load the Apo-LibController
    """
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
        """
        !do not use this method directly!
        Refreshes the class with the current state of the library
        :param lib: The library class
        :return: None
        """
        self.lib = lib
        self.utils = lib.utils

    async def ensure_controller(self, first_loop: bool = True):
        """
        Ensures that the Apo-LibController is loaded
        """
        while True:
            if first_loop:
                if not await self._wait_load(delay=5, retries=5, first_loop=first_loop) and not self._controller_refresh():
                    await self._init_controller()
                first_loop = False
            elif not self._controller_refresh():
                await self._init_controller()
            await asyncio.sleep(5)

    async def _init_controller(self):
        """
        Initializes the Apo-LibController downnload and load
        """
        self.utils.log(logging.DEBUG, self._libclassname, "Attempting to load ApoLibController from GitHub.")
        controller_loaded = await self._load_github()
        if controller_loaded:
            return controller_loaded
        self._controller_found = False
        return None

    def _controller_refresh(self):
        """
        Checks if the Apo-LibController is loaded
        """
        self._controller_found = bool(self.lib.lookup("Apo-LibController"))
        return self._controller_found

    async def _load_github(self):
        """
        Downloads the Apo-LibController from GitHub
        """
        link = (
            "https://raw.githubusercontent.com/anon97945/hikka-mods/lib_test/apolib_controller.py"
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

    async def _wait_load(
        self,
        delay,
        retries,
        first_loop=False
    ):
        """
        Waits for the Apo-LibController to load
        :param delay: The delay between retries
        :param retries: The number of retries
        :param first_loop: Whether this is the first loop
        :return: Whether the Apo-LibController was loaded
        """
        while retries:
            if lib_controller := self.lib.lookup("Apo-LibController"):
                self.utils.log(logging.DEBUG, self._libclassname, "ApoLibController found!")
                return lib_controller
            if not getattr(self.lib.lookup("Loader"), "_fully_loaded", False):
                retries = 1
            elif getattr(self.lib.lookup("Loader"), "_fully_loaded", False) and first_loop:
                retries = 0
            else:
                retries -= 1
            if retries != 0:
                self.utils.log(
                    logging.DEBUG,
                    self._libclassname,
                    "ApoLibController not found, retrying in %s seconds..."
                    "\nHikka fully loaded: %s", delay, getattr(self.lib.lookup("Loader"), "_fully_loaded", False)
                )
            await asyncio.sleep(delay)


class ApodiktumUtils(loader.Module):
    """
    This class is used to handle all the utility functions of the library.
    """
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
        """
        !do not use this method directly!
        Refreshes the class with the current state of the library
        :param lib: The library class
        :return: None
        """
        self.lib = lib
        self.utils = lib.utils

    def get_str(
        self,
        string: str,
        all_strings: dict,
        message: Message
    ) -> str:
        """
        Get a string from a dictionary
        :param string: The string to get
        :param all_strings: The dictionary to get the string from
        :param message: The message to check for forced chat strings
        :return: The translated string
        """
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
        """
        Logs a message to the console
        :param level: The logging level
        :param name: The name of the module
        :param message: The message to log
        :param args: Any additional arguments
        :param kwargs: Any additional keyword arguments
        :param debug_msg: Whether to log the message as a defined debug message
        :return: None
        """
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
    ) -> bool:
        """
        Checks if a user is a member of a chat
        :param chat_id: Chat ID
        :param user_id: User ID
        :return: True if user is a member of the chat, False otherwise
        """
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
    ) -> str:
        """
        Get the tag of a user/channel
        :param user: User/Channel
        :param WithID: Return the tag with the ID
        :return: Tag message as string
        """
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
        """
        Returns a tag link to the user's profile
        :param user: User or user ID
        :return: Tag link as string
        """
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
    ) -> str:
        """
        Gets the invite link for the chat (need to be admin and invite user perms)
        :param chat: Chat or chat ID
        :return: Invite link as string
        """
        if isinstance(chat, int):
            chat = await self._client.get_entity(chat)
        if chat.username:
            link = f"https://t.me/{chat.username}"
        elif chat.admin_rights and chat.admin_rights.invite_users:
            link = await self._client(GetFullChannelRequest(channel=chat.id))
            link = link.full_chat.exported_invite.link
        else:
            link = None
        return link

    async def is_linkedchannel(
        self,
        chat_id: int,
        user_id: int,
    ) -> bool:
        """
        Checks if the message is from the linked channel
        :param chat_id: Chat ID
        :param user_id: User ID
        :return: True if the message is from the linked channel, False otherwise
        """
        user = await self._client.get_entity(user_id)
        if not isinstance(user, Channel):
            return False
        full_chat = await self._client(GetFullChannelRequest(channel=user_id))
        if full_chat.full_chat.linked_chat_id:
            return chat_id == int(full_chat.full_chat.linked_chat_id)

    @staticmethod
    def get_entityurls(message: Message) -> list:
        """
        Returns a list of entityurls from the message
        :param message: Message
        :return: list of entityurls
        """
        return [url for ent, url in message.get_entities_text() if isinstance(ent, MessageEntityUrl)]

    @staticmethod
    def get_href_urls(text: str) -> list:
        """
        Returns a list of href urls from the text
        :param text: str
        :return: list of href urls
        """
        return re.findall("href=[\"\'](.*?)[\"\']", text)

    @staticmethod
    def get_urls(text: str) -> list:
        """
        Returns a list of urls from the text
        :param text: str
        :return: list of urls
        """
        URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:\'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
        return re.findall(URL_REGEX, text)

    @staticmethod
    def rem_duplicates_list(s: list) -> list:
        """
        Remove duplicates from list
        :param s: list
        :return: list without duplicates
        """
        return list(dict.fromkeys(s))

    @staticmethod
    def convert_time(t) -> int:
        """
        Tries to export time from text
        :param t: Xs/Xm/Xh/Xd/Xw
        :return: converted time to seconds as integer
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
    def get_ids_from_tglink(link) -> str:
        """
        Get chat ID and message ID from telegram link
        :param link: telegram link
        :return: chat ID and message ID as string
        """
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
        """
        Check if text is only emoji
        :param text: text
        :return: True if text is only emoji, False otherwise
        """
        return not emoji.replace_emoji(text, replace='') if text else False

    @staticmethod
    def rem_emoji(text: str) -> str:
        """
        Remove emoji from text
        :param text: text
        :return: text
        """
        return emoji.replace_emoji(text, replace='')

    @staticmethod
    def distinct_emoji_list(text: str) -> list:
        """
        Get distinct list of emoji from text
        :param text: text
        :return: list of distinct emoji
        """
        return emoji.distinct_emoji_list(text)

    @staticmethod
    def emoji_list(text: str) -> dict:
        """
        Get dict of emoji from text with index positions
        :param text: text
        :return: dict of emoji with index positions
        """
        return emoji.emoji_list(text)

    @staticmethod
    def unescape_html(text: str) -> str:
        """
        Unescape HTML entities
        :param text: text
        :return: text with HTML entities unescaped
        """
        return html.unescape(text)

    @staticmethod
    def escape_html(text: str) -> str:
        """
        Escape HTML entities
        :param text: text
        :return: text with HTML entities escaped
        """
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
    """
    Apodiktum Utils Beta, just for testing purposes
    """
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
        """
        !do not use this method directly!
        Refreshes the class with the current state of the library
        :param lib: The library class
        :return: None
        """
        self.lib = lib
        self.utils = lib.utils


class ApodiktumInternal(loader.Module):
    """
    Apodiktum Internal, just for internal purposes
    """
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
        """
        !do not use this method directly!
        Refreshes the class with the current state of the library
        :param lib: The library class
        :return: None
        """
        self.lib = lib
        self.utils = lib.utils

    async def beta_access(self):
        """
        !do not use this method directly!
        Checks if the user has beta access
        :return: True if the user has beta access, False otherwise
        """
        beta_ids = None
        beta_access = False
        try:
            async for messages in self._client.iter_messages("@apodiktum_modules_news"):
                if messages and isinstance(messages, Message) and "#UtilsBetaAccess" in messages.raw_text:
                    string = messages.raw_text
                    beta_ids = list(map(int, string[string.find("[")+1:string.find("]")].split(',')))
                    if self._client.tg_id in beta_ids:
                        beta_access = True
                break
            return beta_access
        except Exception as exc:  # skipcq: PYL-W0703
            self.utils.log(logging.DEBUG, self._libclassname, "Error while checking beta access: %s", exc)
            return beta_access

    def send_stats(self):
        """
        !do not use this method directly!
        Send anonymous stats to Hikka
        :return: None
        """
        urls = ["https://raw.githubusercontent.com/anon97945/hikka-mods/master/apodiktum_library.py", "https://raw.githubusercontent.com/anon97945/hikka-mods/master/total_users.py"]

        for url in urls:
            asyncio.ensure_future(self.__send_stats_handler(url))

    async def __send_stats_handler(self, url: str, retry: bool = False):
        """
        !do not use this method directly!
        Send anonymous stats to Hikka
        :param url: The url to send to the stats server
        :return: None
        """
        with contextlib.suppress(Exception):
            if (
                getattr(self._db["hikka.main"], "stats", True)
                and url is not None
                and utils.check_url(url)
            ):
                try:
                    if self._db["LoaderMod"] and not self._db["LoaderMod"]["token"]:
                        self._db["LoaderMod"].setdefault(
                            "token",
                            (
                                await self._client.inline_query(
                                    "@hikkamods_bot", "#get_hikka_token"
                                )
                            )[0].title)

                    res = await utils.run_sync(
                        requests.post,
                        "https://heta.hikariatama.ru/stats",
                        data={"url": url},
                        headers={"X-Hikka-Token": self._db["LoaderMod"]["token"]},
                    )
                    if res.status_code == 403:
                        if retry:
                            return

                        if self._db["LoaderMod"] and not self._db["LoaderMod"]["token"]:
                            self._db["LoaderMod"]["token"] = None
                        return await self._send_stats_handler(url, retry=True)
                except Exception as exc:  # skipcq: PYL-W0703
                    self.utils.log(logging.DEBUG, self._libclassname, "Failed to send stats: %s", exc)


class ApodiktumMigrator(loader.Module):
    """
    Apodiktum Migrator, just for migrating purposes
    It is used by the ApodiktumLibrary to migrate settings of modules to the db.
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
        """
        !do not use this method directly!
        Refreshes the class with the current state of the library
        :param lib: The library class
        :return: None
        """
        self.lib = lib
        self.utils = lib.utils

    async def migrate(
        self,
        classname: str,  # type: ignore
        name: str,  # type: ignore
        changes: dict,  # type: ignore
    ):
        """
        Migrates a module
        :param classname: The classname of the module
        :param name: The name of the module
        :param changes: The changes to migrate
        :return: True if the migration was successful, False otherwise
        """
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
        """
        Handles the auto migration of a module
        :param classname: The classname of the module
        :param name: The name of the module
        :param changes: The changes to migrate
        :param auto_migrate: True if the migration should be auto, False otherwise
        :return: True if the migration was successful, False otherwise
        """
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
        """
        !do not use this method directly!
        Forces the set of the hashs
        """
        await self._set_missing_hashs()

    async def check_new_migration(self):
        """
        !do not use this method directly!
        Checks if a new migration is available
        :return: True if a new migration is available, False otherwise
        """
        chash = hashlib.sha256(self._migrate_to.encode('utf-8')).hexdigest()
        return chash not in self.hashs

    async def full_migrated(self):
        """
        !do not use this method directly!
        Checks if the module is fully migrated
        :return: True if the module is fully migrated, False otherwise
        """
        full_migrated = True
        for migration in self._changes:
            chash = hashlib.sha256(migration.encode('utf-8')).hexdigest()
            if chash not in self.hashs:
                full_migrated = False
        return full_migrated

    async def _migrator_func(self):
        """
        !do not use this method directly!
        The migrator function
        :return: True if the migration was successful
        """
        for migration in self._changes:
            chash = hashlib.sha256(migration.encode('utf-8')).hexdigest()
            if chash not in self.hashs:
                old_classname, new_classname, old_name, new_name = await self._get_names(migration)
                for category in self._changes[migration]:
                    await self._copy_config_init(migration, old_classname, new_classname, old_name, new_name, category)
                await self._set_hash(chash)
        return True

    async def _copy_config_init(self, migration, old_classname, new_classname, old_name, new_name, category):
        """
        !do not use this method directly!
        Initializes the copy of the config
        :param migration: The migration
        :param old_classname: The old classname
        :param new_classname: The new classname
        :param old_name: The old name
        :param new_name: The new name
        :param category: The category
        :return: None
        """
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
        """
        !do not use this method directly!
        Gets the names of the module
        :param migration: The migration
        :return: The old classname, the new classname, the old name, the new name"""
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
        """
        !do not use this method directly!
        Gets the changes of the module
        :param changes: The changes
        :return: The old value, the new value"""
        old_value = None
        new_value = None
        for state, value in changes:
            if state == "old":
                old_value = value
            elif state == "new":
                new_value = value
        return old_value, new_value

    async def _migrate_cfg_values(self, migration, category, new_name, new_classname):
        """
        !do not use this method directly!
        Migrates the config values
        :param migration: The migration
        :param category: The category
        :param new_name: The new name
        :param new_classname: The new classname
        :return: None
        """
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
        """
        !do not use this method directly!
        Copies the config
        :param category: The category
        :param old_name: The old name
        :param new_name: The new name
        :param name: The name
        :return: None
        """
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
        """
        !do not use this method directly!
        Deep merges two dictionaries
        :param dct1: The first dictionary
        :param dct2: The second dictionary
        :param override: Whether to override the values
        :return: The merged dictionary
        """
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
        """
        !do not use this method directly!
        Makes the config dynamic
        :param new_name: The new name
        :param new_classname: The new classname
        :return: None
        """
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
        """
        !do not use this method directly!
        Sets the hash
        :param chash: The hash
        :return: None
        """
        self.hashs.append(chash)
        self._db.set(self._classname, "hashs", self.hashs)
        return

    async def _set_missing_hashs(self):
        """
        !do not use this method directly!
        Sets the missing hashes
        :return: None
        """
        for migration in self._changes:
            chash = hashlib.sha256(migration.encode('utf-8')).hexdigest()
            if chash not in self.hashs:
                await self._set_hash(chash)
