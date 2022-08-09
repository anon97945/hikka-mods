__version__ = (1, 1, 4)


# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#           © Copyright 2022
#
#        developed by @anon97945
#
#     https://t.me/apodiktum_modules
#      https://github.com/anon97945
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/gpl-3.0.html

# meta developer: @apodiktum_modules
# meta banner: https://t.me/file_dumbster/11
# meta pic: https://t.me/file_dumbster/13

# scope: hikka_only
# scope: hikka_min 1.3.0

import asyncio
import contextlib
import logging
import time

from telethon.tl.types import Channel, Chat, Message, User

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumAdminToolsMod(loader.Module):
    """
    Toolpack for Channel and Group Admins.
    """

    strings = {
        "name": "Apo-AdminTools",
        "developer": "@anon97945",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_doc_admin_tag_chats": "React to @admin in given chats.",
        "_cfg_doc_ignore_admins": "Wheather to ignore tags from admins.",
        "_cfg_doc_whitelist": (
            "Whether the `admin_tag_chats`-list is a for excluded(True) or"
            " included(False) chats."
        ),
        "admin_tag": "The User {} asked for help.\n{}",
        "admin_tag_reply": "\n\nThe corresponding message from {} is:",
        "admin_tag_reply_msg": "Thanks, the owner of this Bot got informed.",
        "bcu": "BlockChannelUser",
        "bcu_triggered": "{}, you can't write as a channel here.",
        "bf_triggered": "{}, floodlimit exceeded.",
        "bdl": "BlockDoubleLinks",
        "bgs": "BlockGifSpam",
        "bf": "BlockFlood",
        "bnd": "BlockNonDiscussion",
        "bnd_triggered": (
            "{}, the comments are limited to discussiongroup members, "
            "please join our discussiongroup first."
            "\n\n👉🏻 {}\n\nRespectfully, the admins."
        ),
        "bss": "BlockStickerSpam",
        "error": "<b>Your command was wrong.</b>",
        "gl": "GroupLogger",
        "refresh_chat": "<b>[AdminTools]</b> Chat cache refreshed.",
        "no_id": "<b>Your input was no TG ID.</b>",
        "no_int": "<b>Your input was no Integer.</b>",
        "not_dc": "<b>This is no Groupchat.</b>",
        "permerror": "<b>You have no delete permissions in this chat.</b>",
        "prot_db_string": (
            "<b>[{}]</b> Current Database:\n\nWatcher:\n<code>{}</code>"
            "\n\nChatsettings:\n<code>{}</code>"
        ),
        "prot_settings": (
            "<b>[{}]</b> Current settings in this chat are:\n<code>{}</code>"
        ),
        "prot_start": "<b>[{}]</b> Activated in this chat.</b>",
        "prot_stopped": "<b>[{}]</b> Deactivated in this chat.</b>",
        "prot_turned_off": "<b>[{}]</b> The module is now turned off in all chats.</b>",
    }

    strings_en = {}

    strings_de = {
        "_cfg_cst_auto_migrate": (
            "Ob definierte Änderungen beim Start automatisch migriert werden sollen."
        ),
        "_cfg_doc_admin_tag_chats": "Reagieren Sie in bestimmten Chats auf @admin.",
        "_cls_doc": "Toolpack für Kanal- und Gruppenadministratoren.",
        "admin_tag": "Der Benutzer {} hat um Hilfe gebeten.\n{}",
        "admin_tag_reply": "\n\nDie entsprechende Nachricht von {} ist:",
        "admin_tag_reply_msg": "Danke, der Besitzer dieses Bots wurde informiert.",
        "bcu_triggered": "{}, du kannst hier nicht als Kanal schreiben.",
        "bnd_triggered": (
            "{}, die Kommentarfunktion wurde auf die Chatmitglieder begrenzt, "
            "tritt bitte zuerst unserem Chat bei."
            "\n\n👉🏻 {}\n\nHochachtungsvoll, die Obrigkeit."
        ),
        "error": "<b>Dein Befehl war falsch.</b>",
        "no_id": "<b>Ihre Eingabe war keine TG ID.</b>",
        "no_int": "<b>Ihre Eingabe war keine Integer.</b>",
        "not_dc": "<b>Dies ist kein Gruppenchat.</b>",
        "permerror": "<b>Sie haben in diesem Chat keine Löschberechtigung.</b>",
        "prot_db_string": (
            "<b>[{} - Settings]</b> Aktuelle"
            " Datenbank:\n\nWatcher:\n<code>{}</code>\n\nChateinstellungen:\n<code>{}</code>"
        ),
        "prot_settings": (
            "<b>[{} - Settings]</b> Aktuelle Einstellungen in"
            " diesem Chat:\n<code>{}</code>"
        ),
        "prot_start": "<b>[{}]</b> In diesem Chat aktiviert.</b>",
        "prot_stopped": "<b>[{}]</b> Der Chat wurde aus der Liste entfernt.</b>",
        "prot_turned_off": "<b>[{}]</b> In allen Chats ausgeschaltet.</b>",
        "refresh_chat": "<b>[AdminTools]</b> Der Chat Cache wurde aktualisiert.",
    }

    strings_ru = {
        "_cls_doc": "Пакет инструментов для администраторов каналов и групп.",
        "_cmd_doc_bcu": (
            " ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬\n ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Переключает"
            " BlockChannelUser для текущего чата.\n.bcu notify <true/false>\n"
            " ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Переключает уведомление.\n.bcu ban"
            " <true/false>\n ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Банит канал.\n.bcu deltimer"
            " <секунды/или 0>\n ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Удаляет уведомление в"
            " считанные секунды. 0, чтобы отключить.\n.bcu settings\n"
            " ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Показывает текущую конфигурацию чата.\n.bcu"
            " db\n ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Показывает текущую базу данных.\n.bcu"
            " clearall\n ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Очищает базу данных от"
            " BlockChannelUser.\n"
        ),
        "_cmd_doc_bnd": (
            " ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬\n ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Переключает"
            " BlockNonDiscussion для текущего чата.\n.bnd notify <true/false>\n"
            " ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Переключает уведомление.\n.bnd mute"
            " <минут/или 0>\n ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Заглушает пользователя на Х"
            " минут. 0 чтобы отключить.\n.bnd deltimer <секунды/или 0>\n"
            " ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Удаляет уведомление в считанные секунды. 0"
            " чтобы отключить.\n.bnd settings\n ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  -"
            " Показывает текущую конфигурацию чата.\n.bnd db\n"
            " ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Показывает текущую базу данных.\n.bnd"
            " clearall\n ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Очищает базу данных от"
            " BlockNonDiscussion.\n"
        ),
        "_cmd_doc_gl": (
            "⁭⁫⁪⁫⁬⁭⁫⁪<chatid> <logchannelid>\n ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  -"
            " Регистрирует чат логирования для выбранного канала.\n.gl rem <chatid>\n"
            " ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Удаляет данный чат из наблюдателя.\n.gl"
            " db\n ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Показывает текущую базу данных.\n.gl"
            " settings\n ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Показывает текущую конфигурацию"
            " чата.\n.gl clearall\n ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Очищает базу данных"
            " от Group/Channel Logger.\n"
        ),
        "_cmd_doc_resfresh_chat": "Обновляет кэш чата в текущем чате.",
        "admin_tag": "Пользователь {} просит помощи.\n{}",
        "admin_tag_reply": "\n\nПересылаемое сообщение от\n{}:",
        "admin_tag_reply_msg": "Спасибо, владелец этого бота был проинформирован.",
        "bcu_triggered": "{}, ты не можешь писать тут от имени канала.",
        "bnd_triggered": (
            "{}, комментарии ограничены для участников группы обсуждения, "
            "Пожалуйста, для начала присоединитесь к нашей группе обсуждения."
            "\n\n👉🏻 {}\n\nС уважением, администраторы."
        ),
        "error": "<b>Неверная команда</b>",
        "no_id": "<b>Ты ввёл не телеграм айди.</b>",
        "no_int": "<b>Введенное значение не является целым числом (int)</b>",
        "not_dc": "<b>Это не групповой чат</b>",
        "permerror": "<b>У вас недосточно прав для удаление сообщений в этом чате</b>",
        "prot_db_string": (
            "<b>[{}]</b> Текущая база"
            " данных:\n\nНаблюдающий:\n<code>{}</code>\n\nНастройки"
            " чата:\n<code>{}</code>"
        ),
        "prot_settings": "<b>[{}]</b> Текущие настройки в этом чате:\n<code>{}</code>",
        "prot_start": "<b>[{}]</b> Активировано в этом чате</b>",
        "prot_stopped": "<b>[{}]</b> Деактивировано в этом чате</b>",
        "prot_turned_off": "<b>[{}]</b> Теперь этот модуль выключен во всех чатах</b>",
        "refresh_chat": "<b>[AdminTools]</b> Кэш чата обновлен.",
    }

    all_strings = {
        "strings": strings,
        "strings_en": strings,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    changes = {
        "migration1": {
            "name": {
                "old": "Apo AdminTools",
                "new": "Apo-AdminTools",
            },
        },
    }

    def __init__(self):
        self._ratelimit = []
        self._global_queue = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "admin_tag",
                ["@admin"],
                doc=lambda: self.strings("_cfg_doc_admin_cst_tag"),
                validator=loader.validators.Series(
                    loader.validators.String(),
                ),
            ),
            loader.ConfigValue(
                "admin_tag_chats",
                doc=lambda: self.strings("_cfg_doc_admin_tag_chats"),
                validator=loader.validators.Series(
                    loader.validators.TelegramID(),
                ),
            ),
            loader.ConfigValue(
                "ignore_admins",
                True,
                doc=lambda: self.strings("_cfg_doc_ignore_admins"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "tag_whitelist",
                False,
                doc=lambda: self.strings("_cfg_doc_whitelist"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "auto_migrate",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClass
        )

    async def client_ready(self):
        self._classname = self.__class__.__name__
        self.apo_lib = await self.import_lib(
            "https://raw.githubusercontent.com/anon97945/hikka-libs/master/apodiktum_library.py",
            suspend_on_error=True,
        )
        self.apo_lib.apodiktum_module()
        await self.apo_lib.migrator.auto_migrate_handler(
            self.__class__.__name__,
            self.strings("name"),
            self.changes,
            self.config["auto_migrate"],
        )
        self._db_migrator()
        self._pt_task = asyncio.ensure_future(self._global_queue_handler())
        self._antiflood = {}
        self._ratelimit_bdl = {}
        self._ratelimit_bss = {}
        self._ratelimit_bgs = {}
        self._ratelimit_notify = {
            "bnd": {},
            "bcu": {},
            "bgs": {},
            "bss": {},
            "bdl": {},
            "bf": {},
        }
        self._msg_handler = {}

    async def on_unload(self):
        with contextlib.suppress(Exception):
            self._pt_task.cancel()

    async def cadmintoolscmd(self, message: Message):
        """
        Open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def refresh_chatcmd(self, message: Message):
        """
        Refresh the chat cache in the current chat.
        """
        chat_id = utils.get_chat_id(message)
        await self.apo_lib.utils.get_fullchannel(chat_id, force_refresh=True)
        return await utils.answer(
            message,
            self.apo_lib.utils.get_str("refresh_chat", self.all_strings, message),
        )

    async def bndcmd(self, message: Message):
        """
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Toggles BlockNonDiscussion for the current chat.
        .bnd notify <true/false>
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Toggles the notification message.
        .bnd mute <minutes/or 0>
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Mutes the user for x minutes. 0 to disable.
        .bnd deltimer <seconds/or 0>
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Deletes the notification message in seconds. 0 to disable.
        .bnd settings
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Shows the current configuration of the chat.
        .bnd db
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Shows the current database.
        .bnd clearall
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Clears the db of BlockNonDiscussion.
        """
        bnd = self._db.get(self._classname, "bnd", [])
        sets = self._db.get(self._classname, "bnd_sets", {})
        args = utils.get_args_raw(message).lower()
        args = str(args).split()
        chat = await self._client.get_entity(message.chat)
        chat_id_str = str(chat.id)

        if args and args[0] == "clearall":
            self._db.set(self._classname, "bnd", [])
            self._db.set(self._classname, "bnd_sets", {})
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_turned_off", self.all_strings, message
                ).format(self.apo_lib.utils.get_str("bnd", self.all_strings, message)),
            )

        if args and args[0] == "db":
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_db_string", self.all_strings, message
                ).format(
                    self.apo_lib.utils.get_str("bnd", self.all_strings, message),
                    bnd,
                    sets,
                ),
            )

        if message.is_private:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("not_dc"),
                self.all_strings,
                message,
            )
            return

        if (
            (chat.admin_rights or chat.creator)
            and not chat.admin_rights.delete_messages
            or not chat.admin_rights
            and not chat.creator
        ) and (args or chat_id_str not in bnd):
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("permerror", self.all_strings, message),
            )

        if not args:
            if chat_id_str not in bnd:
                bnd.append(chat_id_str)
                sets.setdefault(chat_id_str, {})
                sets[chat_id_str].setdefault("notify", True)
                sets[chat_id_str].setdefault("mute", 1)
                sets[chat_id_str].setdefault("deltimer", 60)
                self._db.set(self._classname, "bnd", bnd)
                self._db.set(self._classname, "bnd_sets", sets)
                return await utils.answer(
                    message,
                    self.apo_lib.utils.get_str(
                        "prot_start", self.all_strings, message
                    ).format(
                        self.apo_lib.utils.get_str("bnd", self.all_strings, message)
                    ),
                )
            bnd.remove(chat_id_str)
            self._db.set(self._classname, "bnd", bnd)
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_stopped", self.all_strings, message
                ).format(self.apo_lib.utils.get_str("bnd", self.all_strings, message)),
            )

        if chat_id_str in bnd:
            if args[0] == "notify" and args[1] is not None:
                if not isinstance(self.apo_lib.utils.validate_boolean(args[1]), bool):
                    return await utils.answer(
                        message,
                        self.apo_lib.utils.get_str("error", self.all_strings, message),
                    )
                sets[chat_id_str].update(
                    {"notify": self.apo_lib.utils.validate_boolean(args[1])}
                )
            elif args[0] == "mute" and args[1] is not None and chat_id_str in bnd:
                if not self.apo_lib.utils.validate_integer(args[1]):
                    return await utils.answer(
                        message,
                        self.apo_lib.utils.get_str("no_int", self.all_strings, message),
                    )
                sets[chat_id_str].update({"mute": int(args[1])})
            elif args[0] == "deltimer" and args[1] is not None and chat_id_str in bnd:
                if not self.apo_lib.utils.validate_integer(args[1]):
                    return await utils.answer(
                        message,
                        self.apo_lib.utils.get_str("no_int", self.all_strings, message),
                    )
                sets[chat_id_str].update({"deltimer": int(args[1])})
            elif args[0] != "settings" and chat_id_str in bnd:
                return
            self._db.set(self._classname, "bnd", bnd)
            self._db.set(self._classname, "bnd_sets", sets)
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_settings", self.all_strings, message
                ).format(
                    self.apo_lib.utils.get_str("bnd", self.all_strings, message),
                    sets[chat_id_str],
                ),
            )

    async def bfcmd(self, message: Message):
        """
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Toggles BlockFlood for the current chat.
        .bf notify <true/false>
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Toggles the notification message.
        .bf mute <minutes/or 0>
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Mutes the user for x minutes. 0 to disable.
        .bf deltimer <seconds/or 0>
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Deletes the notification message in seconds. 0 to disable.
        .bf settings
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Shows the current configuration of the chat.
        .bf db
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Shows the current database.
        .bf clearall
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Clears the db of BlockNonDiscussion.
        """
        bf = self._db.get(self._classname, "bf", [])
        sets = self._db.get(self._classname, "bf_sets", {})
        args = utils.get_args_raw(message).lower()
        args = str(args).split()
        chat = await self._client.get_entity(message.chat)
        chat_id_str = str(chat.id)

        if args and args[0] == "clearall":
            self._db.set(self._classname, "bf", [])
            self._db.set(self._classname, "bf_sets", {})
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_turned_off", self.all_strings, message
                ).format(self.apo_lib.utils.get_str("bf", self.all_strings, message)),
            )

        if args and args[0] == "db":
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_db_string", self.all_strings, message
                ).format(
                    self.apo_lib.utils.get_str("bf", self.all_strings, message),
                    bf,
                    sets,
                ),
            )

        if message.is_private:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("not_dc"),
                self.all_strings,
                message,
            )
            return

        if (
            (chat.admin_rights or chat.creator)
            and not chat.admin_rights.delete_messages
            or not chat.admin_rights
            and not chat.creator
        ) and (args or chat_id_str not in bf):
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("permerror", self.all_strings, message),
            )

        if not args:
            if chat_id_str not in bf:
                bf.append(chat_id_str)
                sets.setdefault(chat_id_str, {})
                sets[chat_id_str].setdefault("notify", True)
                sets[chat_id_str].setdefault("mute", 5)
                sets[chat_id_str].setdefault("deltimer", 60)
                sets[chat_id_str].setdefault("limit", 8)
                self._db.set(self._classname, "bf", bf)
                self._db.set(self._classname, "bf_sets", sets)
                return await utils.answer(
                    message,
                    self.apo_lib.utils.get_str(
                        "prot_start", self.all_strings, message
                    ).format(
                        self.apo_lib.utils.get_str("bf", self.all_strings, message)
                    ),
                )
            bf.remove(chat_id_str)
            self._db.set(self._classname, "bf", bf)
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_stopped", self.all_strings, message
                ).format(self.apo_lib.utils.get_str("bf", self.all_strings, message)),
            )

        if chat_id_str in bf:
            if args[0] == "notify" and args[1] is not None:
                if not isinstance(self.apo_lib.utils.validate_boolean(args[1]), bool):
                    return await utils.answer(
                        message,
                        self.apo_lib.utils.get_str("error", self.all_strings, message),
                    )
                sets[chat_id_str].update(
                    {"notify": self.apo_lib.utils.validate_boolean(args[1])}
                )
            elif args[0] == "mute" and args[1] is not None and chat_id_str in bf:
                if not self.apo_lib.utils.validate_integer(args[1]):
                    return await utils.answer(
                        message,
                        self.apo_lib.utils.get_str("no_int", self.all_strings, message),
                    )
                sets[chat_id_str].update({"mute": int(args[1])})
            elif args[0] == "limit" and args[1] is not None and chat_id_str in bf:
                if not self.apo_lib.utils.validate_integer(args[1]):
                    return await utils.answer(
                        message,
                        self.apo_lib.utils.get_str("no_int", self.all_strings, message),
                    )
                sets[chat_id_str].update({"limit": int(args[1])})
            elif args[0] == "deltimer" and args[1] is not None and chat_id_str in bf:
                if not self.apo_lib.utils.validate_integer(args[1]):
                    return await utils.answer(
                        message,
                        self.apo_lib.utils.get_str("no_int", self.all_strings, message),
                    )
                sets[chat_id_str].update({"deltimer": int(args[1])})
            elif args[0] != "settings" and chat_id_str in bf:
                return
            self._db.set(self._classname, "bf", bf)
            self._db.set(self._classname, "bf_sets", sets)
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_settings", self.all_strings, message
                ).format(
                    self.apo_lib.utils.get_str("bf", self.all_strings, message),
                    sets[chat_id_str],
                ),
            )

    async def bcucmd(self, message: Message):
        """
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Toggles BlockChannelUser for the current chat.
        .bcu notify <true/false>
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Toggles the notification message.
        .bcu ban <true/false>
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Bans the channel.
        .bcu deltimer <seconds/or 0>
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Deletes the notification message in seconds. 0 to disable.
        .bcu settings
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Shows the current configuration of the chat.
        .bcu db
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Shows the current database.
        .bcu clearall
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Clears the db of BlockChannelUser.
        """
        bcu = self._db.get(self._classname, "bcu", [])
        sets = self._db.get(self._classname, "bcu_sets", {})
        args = utils.get_args_raw(message).lower().split()
        chat = await self._client.get_entity(message.peer_id)
        chat_id_str = str(chat.id)

        if args and args[0] == "clearall":
            self._db.set(self._classname, "bcu", [])
            self._db.set(self._classname, "bcu_sets", {})
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_turned_off", self.all_strings, message
                ).format(self.apo_lib.utils.get_str("bcu", self.all_strings, message)),
            )

        if args and args[0] == "db":
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_db_string", self.all_strings, message
                ).format(
                    self.apo_lib.utils.get_str("bcu", self.all_strings, message),
                    bcu,
                    sets,
                ),
            )

        if message.is_private:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("not_dc", self.all_strings, message),
            )
            return

        if (
            (chat.admin_rights or chat.creator)
            and not chat.admin_rights.delete_messages
            or not chat.admin_rights
            and not chat.creator
        ) and (args or chat_id_str not in bcu):
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("permerror", self.all_strings, message),
            )

        if not args:
            if chat_id_str not in bcu:
                bcu.append(chat_id_str)
                sets.setdefault(chat_id_str, {})
                sets[chat_id_str].setdefault("notify", True)
                sets[chat_id_str].setdefault("ban", True)
                sets[chat_id_str].setdefault("deltimer", 60)
                self._db.set(self._classname, "bcu", bcu)
                self._db.set(self._classname, "bcu_sets", sets)
                return await utils.answer(
                    message,
                    self.apo_lib.utils.get_str(
                        "prot_start", self.all_strings, message
                    ).format(
                        self.apo_lib.utils.get_str("bcu", self.all_strings, message)
                    ),
                )
            bcu.remove(chat_id_str)
            self._db.set(self._classname, "bcu", bcu)
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_stopped", self.all_strings, message
                ).format(self.apo_lib.utils.get_str("bcu", self.all_strings, message)),
            )

        if chat_id_str in bcu:
            if args[0] == "notify" and args[1] is not None:
                if not isinstance(self.apo_lib.utils.validate_boolean(args[1]), bool):
                    return await utils.answer(
                        message,
                        self.apo_lib.utils.get_str("error", self.all_strings, message),
                    )
                sets[chat_id_str].update(
                    {"notify": self.apo_lib.utils.validate_boolean(args[1])}
                )
            elif args[0] == "ban" and args[1] is not None and chat_id_str in bcu:
                if not isinstance(self.apo_lib.utils.validate_boolean(args[1]), bool):
                    return await utils.answer(
                        message,
                        self.apo_lib.utils.get_str("no_int", self.all_strings, message),
                    )
                sets[chat_id_str].update(
                    {"ban": self.apo_lib.utils.validate_boolean(args[1])}
                )
            elif args[0] == "deltimer" and args[1] is not None and chat_id_str in bcu:
                if not self.apo_lib.utils.validate_integer(args[1]):
                    return await utils.answer(
                        message,
                        self.apo_lib.utils.get_str("no_int", self.all_strings, message),
                    )
                sets[chat_id_str].update({"deltimer": int(args[1])})
            elif args[0] != "settings" and chat_id_str in bcu:
                return
            self._db.set(self._classname, "bcu", bcu)
            self._db.set(self._classname, "bcu_sets", sets)
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_settings", self.all_strings, message
                ).format(
                    self.apo_lib.utils.get_str("bcu", self.all_strings, message),
                    sets[chat_id_str],
                ),
            )

    async def bdlcmd(self, message: Message):
        """
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Toggles BlockDoubleLinks for the current chat.
        .bdl timeout <seconds>
           - Sets the timeout for the double links.
        .bdl notify <true/false>
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Toggles the notification message.
        .bdl deltimer <seconds/or 0>
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Deletes the notification message in seconds. 0 to disable.
        .bdl settings
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Shows the current configuration of the chat.
        .bdl db
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Shows the current database.
        .bdl clearall
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Clears the db of BlockChannelUser.
        """
        bdl = self._db.get(self._classname, "bdl", [])
        sets = self._db.get(self._classname, "bdl_sets", {})
        args = utils.get_args_raw(message).lower().split()
        chat = await self._client.get_entity(message.peer_id)
        chat_id_str = str(chat.id)

        if args and args[0] == "clearall":
            self._db.set(self._classname, "bdl", [])
            self._db.set(self._classname, "bdl_sets", {})
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_turned_off", self.all_strings, message
                ).format(self.apo_lib.utils.get_str("bdl", self.all_strings, message)),
            )

        if args and args[0] == "db":
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_db_string", self.all_strings, message
                ).format(
                    self.apo_lib.utils.get_str("bdl", self.all_strings, message),
                    bdl,
                    sets,
                ),
            )

        if message.is_private:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("not_dc", self.all_strings, message),
            )
            return

        if (
            (chat.admin_rights or chat.creator)
            and not chat.admin_rights.delete_messages
            or not chat.admin_rights
            and not chat.creator
        ) and (args or chat_id_str not in bdl):
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("permerror", self.all_strings, message),
            )

        if not args:
            if chat_id_str not in bdl:
                bdl.append(chat_id_str)
                sets.setdefault(chat_id_str, {})
                sets[chat_id_str].setdefault("notify", True)
                sets[chat_id_str].setdefault("timeout", 3600)
                sets[chat_id_str].setdefault("deltimer", 60)
                self._db.set(self._classname, "bdl", bdl)
                self._db.set(self._classname, "bdl_sets", sets)
                return await utils.answer(
                    message,
                    self.apo_lib.utils.get_str(
                        "prot_start", self.all_strings, message
                    ).format(
                        self.apo_lib.utils.get_str("bdl", self.all_strings, message)
                    ),
                )
            bdl.remove(chat_id_str)
            self._db.set(self._classname, "bdl", bdl)
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_stopped", self.all_strings, message
                ).format(self.apo_lib.utils.get_str("bdl", self.all_strings, message)),
            )

        if chat_id_str in bdl:
            if args[0] == "notify" and args[1] is not None:
                if not isinstance(self.apo_lib.utils.validate_boolean(args[1]), bool):
                    return await utils.answer(
                        message,
                        self.apo_lib.utils.get_str("error", self.all_strings, message),
                    )
                sets[chat_id_str].update(
                    {"notify": self.apo_lib.utils.validate_boolean(args[1])}
                )
            elif args[0] == "timeout" and args[1] is not None and chat_id_str in bdl:
                if not self.apo_lib.utils.validate_integer(args[1]):
                    return await utils.answer(
                        message,
                        self.apo_lib.utils.get_str("no_int", self.all_strings, message),
                    )
                sets[chat_id_str].update({"timeout": int(args[1])})
            elif args[0] == "deltimer" and args[1] is not None and chat_id_str in bdl:
                if not self.apo_lib.utils.validate_integer(args[1]):
                    return await utils.answer(
                        message,
                        self.apo_lib.utils.get_str("no_int", self.all_strings, message),
                    )
                sets[chat_id_str].update({"deltimer": int(args[1])})
            elif args[0] != "settings" and chat_id_str in bdl:
                return
            self._db.set(self._classname, "bdl", bdl)
            self._db.set(self._classname, "bdl_sets", sets)
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_settings", self.all_strings, message
                ).format(
                    self.apo_lib.utils.get_str("bdl", self.all_strings, message),
                    sets[chat_id_str],
                ),
            )

    async def bsscmd(self, message: Message):
        """
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Toggles BlockStickerSpam for the current chat.
        .bss timeout <seconds>
           - Sets the timeout for the sticker spam.
        .bss notify <true/false>
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Toggles the notification message.
        .bss deltimer <seconds/or 0>
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Deletes the notification message in seconds. 0 to disable.
        .bss settings
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Shows the current configuration of the chat.
        .bss db
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Shows the current database.
        .bss clearall
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Clears the db of BlockChannelUser.
        """
        bss = self._db.get(self._classname, "bss", [])
        sets = self._db.get(self._classname, "bss_sets", {})
        args = utils.get_args_raw(message).lower().split()
        chat = await self._client.get_entity(message.peer_id)
        chat_id_str = str(chat.id)

        if args and args[0] == "clearall":
            self._db.set(self._classname, "bss", [])
            self._db.set(self._classname, "bss_sets", {})
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_turned_off", self.all_strings, message
                ).format(self.apo_lib.utils.get_str("bss", self.all_strings, message)),
            )

        if args and args[0] == "db":
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_db_string", self.all_strings, message
                ).format(
                    self.apo_lib.utils.get_str("bss", self.all_strings, message),
                    bss,
                    sets,
                ),
            )

        if message.is_private:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("not_dc", self.all_strings, message),
            )
            return

        if (
            (chat.admin_rights or chat.creator)
            and not chat.admin_rights.delete_messages
            or not chat.admin_rights
            and not chat.creator
        ) and (args or chat_id_str not in bss):
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("permerror", self.all_strings, message),
            )

        if not args:
            if chat_id_str not in bss:
                bss.append(chat_id_str)
                sets.setdefault(chat_id_str, {})
                sets[chat_id_str].setdefault("notify", True)
                sets[chat_id_str].setdefault("timeout", 300)
                sets[chat_id_str].setdefault("deltimer", 60)
                self._db.set(self._classname, "bss", bss)
                self._db.set(self._classname, "bss_sets", sets)
                return await utils.answer(
                    message,
                    self.apo_lib.utils.get_str(
                        "prot_start", self.all_strings, message
                    ).format(
                        self.apo_lib.utils.get_str("bss", self.all_strings, message)
                    ),
                )
            bss.remove(chat_id_str)
            self._db.set(self._classname, "bss", bss)
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_stopped", self.all_strings, message
                ).format(self.apo_lib.utils.get_str("bss", self.all_strings, message)),
            )

        if chat_id_str in bss:
            if args[0] == "notify" and args[1] is not None:
                if not isinstance(self.apo_lib.utils.validate_boolean(args[1]), bool):
                    return await utils.answer(
                        message,
                        self.apo_lib.utils.get_str("error", self.all_strings, message),
                    )
                sets[chat_id_str].update(
                    {"notify": self.apo_lib.utils.validate_boolean(args[1])}
                )
            elif args[0] == "timeout" and args[1] is not None and chat_id_str in bss:
                if not self.apo_lib.utils.validate_integer(args[1]):
                    return await utils.answer(
                        message,
                        self.apo_lib.utils.get_str("no_int", self.all_strings, message),
                    )
                sets[chat_id_str].update({"timeout": int(args[1])})
            elif args[0] == "deltimer" and args[1] is not None and chat_id_str in bss:
                if not self.apo_lib.utils.validate_integer(args[1]):
                    return await utils.answer(
                        message,
                        self.apo_lib.utils.get_str("no_int", self.all_strings, message),
                    )
                sets[chat_id_str].update({"deltimer": int(args[1])})
            elif args[0] != "settings" and chat_id_str in bss:
                return
            self._db.set(self._classname, "bss", bss)
            self._db.set(self._classname, "bss_sets", sets)
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_settings", self.all_strings, message
                ).format(
                    self.apo_lib.utils.get_str("bss", self.all_strings, message),
                    sets[chat_id_str],
                ),
            )

    async def bgscmd(self, message: Message):
        """
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Toggles BlockStickerSpam for the current chat.
        .bgs timeout <seconds>
           - Sets the timeout for the sticker spam.
        .bgs notify <true/false>
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Toggles the notification message.
        .bgs deltimer <seconds/or 0>
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Deletes the notification message in seconds. 0 to disable.
        .bgs settings
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Shows the current configuration of the chat.
        .bgs db
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Shows the current database.
        .bgs clearall
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Clears the db of BlockChannelUser.
        """
        bgs = self._db.get(self._classname, "bgs", [])
        sets = self._db.get(self._classname, "bgs_sets", {})
        args = utils.get_args_raw(message).lower().split()
        chat = await self._client.get_entity(message.peer_id)
        chat_id_str = str(chat.id)

        if args and args[0] == "clearall":
            self._db.set(self._classname, "bgs", [])
            self._db.set(self._classname, "bgs_sets", {})
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_turned_off", self.all_strings, message
                ).format(self.apo_lib.utils.get_str("bgs", self.all_strings, message)),
            )

        if args and args[0] == "db":
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_db_string", self.all_strings, message
                ).format(
                    self.apo_lib.utils.get_str("bgs", self.all_strings, message),
                    bgs,
                    sets,
                ),
            )

        if message.is_private:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("not_dc", self.all_strings, message),
            )
            return

        if (
            (chat.admin_rights or chat.creator)
            and not chat.admin_rights.delete_messages
            or not chat.admin_rights
            and not chat.creator
        ) and (args or chat_id_str not in bgs):
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("permerror", self.all_strings, message),
            )

        if not args:
            if chat_id_str not in bgs:
                bgs.append(chat_id_str)
                sets.setdefault(chat_id_str, {})
                sets[chat_id_str].setdefault("notify", True)
                sets[chat_id_str].setdefault("timeout", 300)
                sets[chat_id_str].setdefault("deltimer", 60)
                self._db.set(self._classname, "bgs", bgs)
                self._db.set(self._classname, "bgs_sets", sets)
                return await utils.answer(
                    message,
                    self.apo_lib.utils.get_str(
                        "prot_start", self.all_strings, message
                    ).format(
                        self.apo_lib.utils.get_str("bgs", self.all_strings, message)
                    ),
                )
            bgs.remove(chat_id_str)
            self._db.set(self._classname, "bgs", bgs)
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_stopped", self.all_strings, message
                ).format(self.apo_lib.utils.get_str("bgs", self.all_strings, message)),
            )

        if chat_id_str in bgs:
            if args[0] == "notify" and args[1] is not None:
                if not isinstance(self.apo_lib.utils.validate_boolean(args[1]), bool):
                    return await utils.answer(
                        message,
                        self.apo_lib.utils.get_str("error", self.all_strings, message),
                    )
                sets[chat_id_str].update(
                    {"notify": self.apo_lib.utils.validate_boolean(args[1])}
                )
            elif args[0] == "timeout" and args[1] is not None and chat_id_str in bgs:
                if not self.apo_lib.utils.validate_integer(args[1]):
                    return await utils.answer(
                        message,
                        self.apo_lib.utils.get_str("no_int", self.all_strings, message),
                    )
                sets[chat_id_str].update({"timeout": int(args[1])})
            elif args[0] == "deltimer" and args[1] is not None and chat_id_str in bgs:
                if not self.apo_lib.utils.validate_integer(args[1]):
                    return await utils.answer(
                        message,
                        self.apo_lib.utils.get_str("no_int", self.all_strings, message),
                    )
                sets[chat_id_str].update({"deltimer": int(args[1])})
            elif args[0] != "settings" and chat_id_str in bgs:
                return
            self._db.set(self._classname, "bgs", bgs)
            self._db.set(self._classname, "bgs_sets", sets)
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_settings", self.all_strings, message
                ).format(
                    self.apo_lib.utils.get_str("bgs", self.all_strings, message),
                    sets[chat_id_str],
                ),
            )

    async def glcmd(self, message: Message):
        """
        <chatid> <logchannelid>
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Logs given groupchat in given channel.
        .gl rem <chatid>
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Removes given chat from watcher.
        .gl db
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Shows the current database.
        .gl settings
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Shows the current configuration of the chat.
        .gl clearall
         ⁭⁫⁪⁫⁬⁭⁫⁪⁭⁫⁪⁫⁬⁭⁫⁪⁫⁬  - Clears the db of Group/Channel Logger.
        """
        gl = self._db.get(self._classname, "gl", [])
        sets = self._db.get(self._classname, "gl_sets", {})
        args = utils.get_args_raw(message).lower().split()
        chat_id = utils.get_chat_id(message)

        if not args:
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("error", self.all_strings, message),
            )

        if args[0] == "clearall":
            self._db.set(self._classname, "gl", [])
            self._db.set(self._classname, "gl_sets", {})
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_turned_off", self.all_strings, message
                ).format(self.apo_lib.utils.get_str("gl", self.all_strings, message)),
            )
        if args[0] == "db":
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_db_string", self.all_strings, message
                ).format(
                    self.apo_lib.utils.get_str("gl", self.all_strings, message),
                    gl,
                    sets,
                ),
            )
        if args[0] is not None and self.apo_lib.utils.validate_tgid(args[0]):
            chat_id = args[0]
        elif args[0] == "rem":
            chat_id = args[1]
        elif args[0] == "db":
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_db_string", self.all_strings, message
                ).format(
                    self.apo_lib.utils.get_str("gl", self.all_strings, message), sets
                ),
            )
        elif args[0] not in ["clearall", "settings"]:
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("error", self.all_strings, message),
            )
        elif not args:
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("error", self.all_strings, message),
            )
        if (
            args[0] == "rem"
            and self.apo_lib.utils.validate_tgid(args[1])
            and chat_id in gl
        ):
            gl.remove(chat_id)
            self._db.set(self._classname, "gl", gl)
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_stopped", self.all_strings, message
                ).format(self.apo_lib.utils.get_str("gl", self.all_strings, message)),
            )
        if args[0] == "rem" and (
            self.apo_lib.utils.validate_tgid(args[1]) or chat_id not in gl
        ):
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("error", self.all_strings, message),
            )
        if not self.apo_lib.utils.validate_tgid(chat_id):
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("error", self.all_strings, message),
            )
        if chat_id not in gl:
            if not self.apo_lib.utils.validate_tgid(
                args[0]
            ) or not self.apo_lib.utils.validate_tgid(args[1]):
                return await utils.answer(
                    message,
                    self.apo_lib.utils.get_str("no_id", self.all_strings, message),
                )
            gl.append(chat_id)
            sets.setdefault(chat_id, {})
            sets[chat_id].setdefault("logchannel", args[1])
            self._db.set(self._classname, "gl", gl)
            self._db.set(self._classname, "gl_sets", sets)
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "prot_start", self.all_strings, message
                ).format(self.apo_lib.utils.get_str("gl", self.all_strings, message)),
            )
        if len(args) == 2:
            if not self.apo_lib.utils.validate_tgid(
                args[0]
            ) or not self.apo_lib.utils.validate_tgid(args[1]):
                return await utils.answer(
                    message,
                    self.apo_lib.utils.get_str("no_id", self.all_strings, message),
                )
            sets[chat_id].update({"logchannel": args[1]})
        elif args[0] != "settings" and chat_id in gl:
            return
        self._db.set(self._classname, "gl", gl)
        self._db.set(self._classname, "gl_sets", sets)
        return await utils.answer(
            message,
            self.apo_lib.utils.get_str(
                "prot_settings", self.all_strings, message
            ).format(
                self.apo_lib.utils.get_str("gl", self.all_strings, message),
                sets[chat_id],
            ),
        )

    async def p__bnd_handler(
        self,
        chat: Chat,
        user: User,
        message: Message,
        bnd: list,
        bnd_sets: dict,
    ):  # sourcery skip: low-code-quality
        """
        Block users which are not members of the group.
        :param chat: Chat object.
        :param user: User object.
        :param message: Message object.
        :param bnd: List of watched groups.
        :param bnd_sets: Dictionary of group IDs and their settings.
        """
        if str(chat.id) not in bnd or message.id in self._msg_handler:
            return
        self._msg_handler = {message.id: "p__bnd"}
        asyncio.ensure_future(self.p__bnd(chat, user, message, bnd_sets))
        return

    async def p__bnd(
        self, chat: Chat, user: User, message: Message, bnd_sets: dict
    ):  # sourcery skip: low-code-quality
        await self.apo_lib.utils.delete_message(message, True)
        if (
            chat.admin_rights.ban_users
            and bnd_sets[str(chat.id)].get("mute") is not None
            and bnd_sets[str(chat.id)].get("mute") != 0
        ):
            duration = bnd_sets[str(chat.id)].get("mute")
            await self.apo_lib.utils.mute(chat.id, user.id, duration)
        if bnd_sets[str(chat.id)].get("notify") is True and (
            not self._ratelimit_notify["bnd"].get(user.id)
            or self._ratelimit_notify["bnd"].get(user.id) < time.time()
        ):
            for key, value in list(self._ratelimit_notify["bnd"].items()):
                if value < time.time():
                    self._ratelimit_notify["bnd"].pop(key)
            self._ratelimit_notify["bnd"].update(
                {
                    user.id: time.time() + bnd_sets[str(chat.id)].get("deltimer")
                    if bnd_sets[str(chat.id)].get("deltimer") != 0
                    else time.time() + 15
                }
            )
            usertag = await self.apo_lib.utils.get_tag(user, True)
            link = await self.apo_lib.utils.get_invite_link(chat)
            if message.is_reply:
                reply = await self.apo_lib.utils.get_first_msg(message)
            else:
                reply = None
            if reply and not isinstance(
                await self._client.get_entity(reply.sender_id), Channel
            ):
                reply = None
            if await self.apo_lib.utils.check_inlinebot(chat.id):
                msg = await self.inline.bot.send_message(
                    chat.id
                    if str(chat.id).startswith("-100")
                    else int(f"-100{chat.id}"),
                    self.apo_lib.utils.get_str(
                        "bnd_triggered", self.all_strings, message
                    ).format(usertag, link),
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_to_message_id=getattr(reply, "id", None),
                    allow_sending_without_reply=True,
                )
            else:
                msg = await utils.answer(
                    message,
                    self.apo_lib.utils.get_str(
                        "bnd_triggered", self.all_strings, message
                    ).format(usertag, link),
                )
            if bnd_sets[str(chat.id)].get("deltimer") != 0:
                deltimer = bnd_sets[str(chat.id)].get("deltimer")
                await self.apo_lib.utils.delete_message(msg, deltimer=deltimer)

    async def p__bcu_handler(
        self,
        chat: Chat,
        user: User,
        message: Message,
        bcu: list,
        bcu_sets: dict,
    ):
        """
        Block Channel Users.
        :param chat: Chat object.
        :param user: User object.
        :param message: Message object.
        :param bcu: List of watched groups.
        :param bcu_sets: Dictionary of group IDs and their settings.
        """
        if str(chat.id) not in bcu or message.id in self._msg_handler:
            return
        self._msg_handler = {message.id: "p__bcu"}
        asyncio.ensure_future(self.p__bcu(chat, user, message, bcu_sets))
        return

    async def p__bcu(self, chat, user, message, bcu_sets):
        await self.apo_lib.utils.delete_message(message)
        if bcu_sets[str(chat.id)].get("ban") is True:
            await self.apo_lib.utils.ban(chat.id, user.id)
        if bcu_sets[str(chat.id)].get("notify") is True and (
            not self._ratelimit_notify["bcu"].get(user.id)
            or self._ratelimit_notify["bcu"].get(user.id) < time.time()
        ):
            for key, value in list(self._ratelimit_notify["bcu"].items()):
                if value < time.time():
                    self._ratelimit_notify["bcu"].pop(key)
            self._ratelimit_notify["bcu"].update(
                {
                    user.id: time.time() + bcu_sets[str(chat.id)].get("deltimer")
                    if bcu_sets[str(chat.id)].get("deltimer") != 0
                    else time.time() + 15
                }
            )
            usertag = await self.apo_lib.utils.get_tag(user, True)
            reply = (
                await self.apo_lib.utils.get_first_msg(message)
                if message.is_reply
                else None
            )
            if reply and not isinstance(
                await self._client.get_entity(reply.sender_id), Channel
            ):
                reply = None
            if await self.apo_lib.utils.check_inlinebot(chat.id):
                msg = await self.inline.bot.send_message(
                    chat.id
                    if str(chat.id).startswith("-100")
                    else int(f"-100{chat.id}"),
                    self.apo_lib.utils.get_str(
                        "bcu_triggered", self.all_strings, message
                    ).format(usertag),
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_to_message_id=getattr(reply, "id", None),
                    allow_sending_without_reply=True,
                )
            else:
                msg = await utils.answer(
                    message,
                    self.apo_lib.utils.get_str(
                        "bcu_triggered", self.all_strings, message
                    ).format(usertag),
                )
            if bcu_sets[str(chat.id)].get("deltimer") != 0:
                deltimer = bcu_sets[str(chat.id)].get("deltimer")
                await self.apo_lib.utils.delete_message(msg, deltimer=deltimer)

    async def p__bf_handler(
        self,
        chat: Chat,
        user: User,
        message: Message,
        bf: list,
        bf_sets: dict,
    ):  # sourcery skip: low-code-quality
        """
        Block users which are not members of the group.
        :param chat: Chat object.
        :param user: User object.
        :param message: Message object.
        :param bf: List of watched groups.
        :param bf_sets: Dictionary of group IDs and their settings.
        """
        if str(chat.id) not in bf:
            return
        if (
            self._antiflood.get(chat.id)
            and self._antiflood[chat.id][0] == user.id
            and self._antiflood[chat.id][1] >= bf_sets[str(chat.id)].get("limit")
        ):
            asyncio.ensure_future(self.p__bf(chat, user, message, bf_sets))
        else:
            self._antiflood.update(
                {
                    chat.id: [
                        user.id,
                        (
                            self._antiflood[chat.id][1] + 1
                            if self._antiflood.get(chat.id)
                            else 1
                        ),
                    ]
                }
            )

    async def p__bf(
        self,
        chat: Chat,
        user: User,
        message: Message,
        bf_sets: dict,
    ):  # sourcery skip: low-code-quality
        with contextlib.suppress(Exception):
            self._antiflood.pop(chat.id)
        await self.apo_lib.utils.delete_message(message, True)
        if (
            chat.admin_rights.ban_users
            and bf_sets[str(chat.id)].get("mute") is not None
            and bf_sets[str(chat.id)].get("mute") != 0
        ):
            duration = bf_sets[str(chat.id)].get("mute")
            await self.apo_lib.utils.mute(chat.id, user.id, duration)
        if bf_sets[str(chat.id)].get("notify") is True and (
            not self._ratelimit_notify["bf"].get(user.id)
            or self._ratelimit_notify["bf"].get(user.id) < time.time()
        ):
            for key, value in list(self._ratelimit_notify["bf"].items()):
                if value < time.time():
                    self._ratelimit_notify["bf"].pop(key)
            self._ratelimit_notify["bf"].update(
                {
                    user.id: time.time() + bf_sets[str(chat.id)].get("deltimer")
                    if bf_sets[str(chat.id)].get("deltimer") != 0
                    else time.time() + 15
                }
            )
            usertag = await self.apo_lib.utils.get_tag(user, True)
            link = await self.apo_lib.utils.get_invite_link(chat)
            if message.is_reply:
                reply = await self.apo_lib.utils.get_first_msg(message)
            else:
                reply = None
            if reply and not isinstance(
                await self._client.get_entity(reply.sender_id), Channel
            ):
                reply = None
            if await self.apo_lib.utils.check_inlinebot(chat.id):
                msg = await self.inline.bot.send_message(
                    chat.id
                    if str(chat.id).startswith("-100")
                    else int(f"-100{chat.id}"),
                    self.apo_lib.utils.get_str(
                        "bf_triggered", self.all_strings, message
                    ).format(usertag, link),
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_to_message_id=getattr(reply, "id", None),
                    allow_sending_without_reply=True,
                )
            else:
                msg = await utils.answer(
                    message,
                    self.apo_lib.utils.get_str(
                        "bf_triggered", self.all_strings, message
                    ).format(usertag, link),
                )
            if bf_sets[str(chat.id)].get("deltimer") != 0:
                deltimer = bf_sets[str(chat.id)].get("deltimer")
                await self.apo_lib.utils.delete_message(msg, deltimer=deltimer)

    async def p__bdl(
        self,
        chat: Chat,
        message: Message,
        bdl: list,
        bdl_sets: dict,
    ):  # sourcery skip: low-code-quality
        """
        Block double links in a group.
        :param chat: Chat object.
        :param message: Message object.
        :param bdl: List of watched id's.
        :param bdl_sets: Dictionary of group IDs and their settings.
        """
        if str(chat.id) not in bdl or message.id in self._msg_handler:
            return
        url = self.apo_lib.utils.get_all_urls(message.text, rem_duplicates=True)
        url = url[0] if len(url) > 0 else None
        if not url:
            return
        if (
            self._ratelimit_bdl.get(chat.id)
            and url in self._ratelimit_bdl.get(chat.id)
            and self._ratelimit_bdl[chat.id].get(url) > time.time()
        ):
            self._msg_handler = {message.id: "p__bnd"}
            asyncio.ensure_future(self.apo_lib.utils.delete_message(message, True))
            if self._ratelimit_bdl.get(chat.id):
                for key, value in list(self._ratelimit_bdl[chat.id].items()):
                    if value < time.time():
                        self._ratelimit_bdl[chat.id].pop(key)
        else:
            self._ratelimit_bdl.update(
                {chat.id: {url: time.time() + bdl_sets[str(chat.id)].get("timeout")}}
            )

    async def p__bss(
        self,
        chat: Chat,
        user: User,
        message: Message,
        bss: list,
        bss_sets: dict,
    ):  # sourcery skip: low-code-quality
        """
        Block Sticker Spam in a group.
        :param chat: Chat object.
        :param user: User object.
        :param message: Message object.
        :param bss: List of watched id's.
        :param bss_sets: Dictionary of group IDs and their settings.
        """
        if (
            str(chat.id) not in bss
            or not message.sticker
            or message.id in self._msg_handler
        ):
            return
        if (
            self._ratelimit_bss.get(chat.id)
            and user.id in self._ratelimit_bss.get(chat.id)
            and self._ratelimit_bss[chat.id].get(user.id) > time.time()
        ):
            self._msg_handler = {message.id: "p__bss"}
            asyncio.ensure_future(self.apo_lib.utils.delete_message(message, True))
            if self._ratelimit_bss.get(chat.id):
                for key, value in list(self._ratelimit_bss[chat.id].items()):
                    if value < time.time():
                        self._ratelimit_bss[chat.id].pop(key)
        else:
            self._ratelimit_bss.update(
                {
                    chat.id: {
                        user.id: time.time() + bss_sets[str(chat.id)].get("timeout")
                    }
                }
            )

    async def p__bgs(
        self,
        chat: Chat,
        user: User,
        message: Message,
        bgs: list,
        bgs_sets: dict,
    ):  # sourcery skip: low-code-quality
        """
        Block Gif Spam in a group.
        :param chat: Chat object.
        :param user: User object.
        :param message: Message object.
        :param bgs: List of watched id's.
        :param bgs_sets: Dictionary of group IDs and their settings.
        """
        if (
            str(chat.id) not in bgs
            or not message.gif
            or message.id in self._msg_handler
        ):
            return
        if (
            self._ratelimit_bgs.get(chat.id)
            and user.id in self._ratelimit_bgs.get(chat.id)
            and self._ratelimit_bgs[chat.id].get(user.id) > time.time()
        ):
            self._msg_handler = {message.id: "p__bgs"}
            asyncio.ensure_future(self.apo_lib.utils.delete_message(message, True))
            if self._ratelimit_bgs.get(chat.id):
                for key, value in list(self._ratelimit_bgs[chat.id].items()):
                    if value < time.time():
                        self._ratelimit_bgs[chat.id].pop(key)
        else:
            self._ratelimit_bgs.update(
                {
                    chat.id: {
                        user.id: time.time() + bgs_sets[str(chat.id)].get("timeout")
                    }
                }
            )

    async def p__gl(
        self,
        chat: Chat,
        user: User,
        message: Message,
        gl: list,
        gl_sets: dict,
    ):  # sourcery skip: low-code-quality
        """
        Log messages of a group.
        :param chat: Chat object.
        :param user: User object.
        :param message: Message object.
        :param gl: List of group IDs to log.
        :param gl_sets: Dictionary of group IDs and their settings.
        """
        if message.is_private or str(chat.id) not in gl:
            return
        logchan_id = int(gl_sets[str(chat.id)].get("logchannel"))
        chat_tag = await self.apo_lib.utils.get_tag(chat, True)
        user_tag = await self.apo_lib.utils.get_tag(user, True)
        link = (
            f"Chat: {chat_tag} | #ID_{chat.id}" + f"\nUser: {user_tag} | #ID_{user.id}"
        )
        try:
            await message.forward_to(logchan_id)
            await self._client.send_message(logchan_id, link)
        except Exception as exc:  # skipcq: PYL-W0703
            if "FORWARDS_RESTRICTED" in str(exc):
                msgs = await self._client.get_messages(chat.id, ids=message.id)
                await self._client.send_message(logchan_id, message=msgs)
                await self._client.send_message(logchan_id, link)

    async def p__admin_handler(
        self,
        chat: Chat,
        user: User,
        message: Message,
    ):  # sourcery skip: low-code-quality
        """
        Watch for admintag messages
        :param chat: Chat object.
        :param user: User object.
        :param message: Message object
        :return: True if message is admintag
        """
        if (
            message.id in self._msg_handler
            or all(
                cst_tag.lower() not in [x.lower() for x in message.raw_text.split()]
                for cst_tag in self.config["admin_tag"]
            )
            or (
                isinstance(user, User)
                and (perms := await self.apo_lib.utils.is_member(chat.id, user.id))
                and perms.is_admin
            )
        ):
            return
        self._msg_handler = {message.id: "p__admin"}

        asyncio.ensure_future(self.p__admin(chat, user, message))

    async def p__admin(
        self, chat: Chat, user: User, message: Message
    ):  # sourcery skip: low-code-quality
        admin_tag_string = self.apo_lib.utils.get_str(
            "admin_tag", self.all_strings, message
        ).format(
            await self.apo_lib.utils.get_tag(user.id, True),
            await utils.get_message_link(message),
        )
        if message.is_reply:
            reply = await message.get_reply_message()
            reply_user = await self._client.get_entity(reply.sender_id)
            admin_tag_string += self.apo_lib.utils.get_str(
                "admin_tag_reply", self.all_strings, message
            ).format(
                await self.apo_lib.utils.get_tag(reply_user, True),
            )
        else:
            reply = None

        if await self.apo_lib.utils.check_inlinebot(chat.id):
            msg = await self.inline.bot.send_message(
                chat.id if str(chat.id).startswith("-100") else int(f"-100{chat.id}"),
                self.apo_lib.utils.get_str(
                    "admin_tag_reply_msg", self.all_strings, message
                ),
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_to_message_id=message.id,
                allow_sending_without_reply=True,
            )
        else:
            msg = await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "admin_tag_reply_msg", self.all_strings, message
                ),
                reply_to=message,
            )
        await self.inline.bot.send_message(
            self.tg_id,
            admin_tag_string,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        if reply:
            await self.inline.bot.forward_message(
                self.tg_id,
                chat.id if str(chat.id).startswith("-100") else int(f"-100{chat.id}"),
                message_id=reply.id,
            )
        await asyncio.sleep(30)
        await self.apo_lib.utils.delete_message(msg)

    @loader.watcher("only_messages", "only_groups", "only_channels", "in")
    async def watcher_protections(self, message: Message):
        self._global_queue += [message]

    async def _global_queue_handler(self):
        while True:
            while self._global_queue:
                with contextlib.suppress(Exception):
                    await self._global_queue_handler_process(self._global_queue.pop(0))
            await asyncio.sleep(0)

    async def _global_queue_handler_process(self, message: Message):
        # sourcery skip: low-code-quality
        chat_id = utils.get_chat_id(message)
        chat_id_str = str(chat_id)
        user_id = await self.apo_lib.utils.get_user_id(message)
        bcu = self._db.get(self._classname, "bcu", [])
        bcu_sets = self._db.get(self._classname, "bcu_sets", {})
        bdl = self._db.get(self._classname, "bdl", [])
        bdl_sets = self._db.get(self._classname, "bdl_sets", {})
        bf = self._db.get(self._classname, "bf", [])
        bf_sets = self._db.get(self._classname, "bf_sets", {})
        bgs = self._db.get(self._classname, "bgs", [])
        bgs_sets = self._db.get(self._classname, "bgs_sets", {})
        bnd = self._db.get(self._classname, "bnd", [])
        bnd_sets = self._db.get(self._classname, "bnd_sets", {})
        bss = self._db.get(self._classname, "bss", [])
        bss_sets = self._db.get(self._classname, "bss_sets", {})
        if (
            user_id in [chat_id, self.inline.bot_id]
            or (
                chat_id_str in bnd
                or chat_id_str in bcu
                or chat_id_str in bdl
                or chat_id_str in bf
                or chat_id_str in bss
            )
            or (
                (
                    self.config["tag_whitelist"]
                    and chat_id not in self.config["admin_tag_chats"]
                )
                or (
                    not self.config["tag_whitelist"]
                    and chat_id in self.config["admin_tag_chats"]
                )
            )
        ):
            chat = await self._client.get_entity(chat_id)
            user = await self._client.get_entity(user_id)
            if (
                (
                    (not chat.admin_rights or not chat.creator)
                    or not chat.admin_rights.delete_messages
                )
                or (
                    isinstance(user, User)
                    and (perms := await self.apo_lib.utils.is_member(chat_id, user_id))
                    and perms.is_admin
                )
                or (
                    isinstance(user, Channel)
                    and not (perms := None)
                    and await self.apo_lib.utils.is_linkedchannel(chat_id, user_id)
                )
            ):
                return
            await self.p__bf_handler(chat, user, message, bf, bf_sets)
            if isinstance(user, User) and not perms:
                await self.p__bnd_handler(chat, user, message, bnd, bnd_sets)
            if isinstance(user, Channel):
                await self.p__bcu_handler(chat, user, message, bcu, bcu_sets)
            await self.p__bdl(chat, message, bdl, bdl_sets)
            await self.p__bss(chat, user, message, bss, bss_sets)
            await self.p__bgs(chat, user, message, bgs, bgs_sets)
            await self.p__admin_handler(chat, user, message)
        with contextlib.suppress(Exception):
            self._msg_handler.pop(message.id)
        return

    @loader.watcher("only_messages", "only_groups", "only_channels")
    async def watcher_logger(self, message: Message):
        chat_id = utils.get_chat_id(message)
        chat_id_str = str(chat_id)
        user_id = await self.apo_lib.utils.get_user_id(message)
        gl = self._db.get(self._classname, "gl", [])
        gl_sets = self._db.get(self._classname, "gl_sets", {})
        bf = self._db.get(self._classname, "bf", [])
        if chat_id_str in gl:
            chat = await self._client.get_entity(chat_id)
            user = await self._client.get_entity(user_id)
            asyncio.ensure_future(self.p__gl(chat, user, message, gl, gl_sets))
        if (
            chat_id_str in bf
            and self._antiflood.get(chat_id)
            and self._antiflood[chat_id][0] != user_id
        ):
            self._antiflood.pop(chat_id)
        return

    def _db_migrator(self):
        if self._db.get(self._classname, "migrate"):
            return
        for key1, value1 in list(self._db[self._classname].items()):
            if key1 in ["bnd", "bcu", "gl", "bdl", "bss", "bgs"]:
                self._db.set(self._classname, key1, list(map(str, value1)))
            if key1 in [
                "bcu_sets",
                "gl_sets",
                "bnd_sets",
                "bdl_sets",
                "bss_sets",
                "bgs_sets",
            ]:
                for key2, value2 in list(value1.items()):
                    if isinstance(key2, int):
                        self._db[self._classname][key1].pop(key2)
                        self._db[self._classname][key1].update({str(key2): value2})
        for key1, value1 in list(self._db[self._classname].items()):
            if key1 in ["gl_sets"]:
                for key2, value2 in list(value1.items()):
                    for key3, value3 in list(value2.items()):
                        if key3 == "logchannel" and isinstance(value3, int):
                            self._db[self._classname][key1][key2][key3] = str(value3)
        with contextlib.suppress(Exception):
            self._db[self._classname].pop("migrated")
        self._db.set(self._classname, "migrate", True)
