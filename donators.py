__version__ = (0, 0, 7)

# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
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

from telethon.errors import UserNotParticipantError
from telethon.tl.types import Message, Chat, User
from datetime import timedelta, date
from typing import Union

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumDonatorsMod(loader.Module):
    """
    Handle donations in a given channel and kick them after the period of time.
    """
    strings = {
        "name": "Apo Donators",
        "developer": "@anon97945",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_cst_auto_migrate_debug": "Wheather log debug messages of auto migrate.",
        "_cfg_cst_auto_migrate_log": "Wheather log auto migrate as info(True) or debug(False).",
        "_cfg_cst_channel": "The Channel ID where the donations should be saved.",
        "_cfg_cst_custom_message": "The message send to the user after the subscription is added. Use <br> for new line.",
        "_cfg_cst_kickchannel": "The channel ids to kick the user from after the subscription.",
        "_cfg_cst_monthlyamount": "The monthly cost of the subscription.",
        "_cfg_cst_subscription_gift": "The gift to send to the user after the subscription. Will be attached to custom_message. Use <br> for new line.",
        "_cfg_doc_log_kick": "Logs successful kicks from the chats.",
        "_log_doc_kicked": "Kicked {} from {}.",
        "amount": "Amount",
        "code": "Code",
        "date": "Date",
        "donation_saved": "🎉 Donation saved!",
        "dtype": "DonationType",
        "no_amount": "No amount found.",
        "no_args": "No args.",
        "no_channel": "No logchannel set.",
        "no_reply": "You didn't reply to a message.",
        "rank": "Rank",
        "total_amount": "<b><u>Total amount of donations:</u></b>\n{}",
        "uname": "Name",
        "userid": "UserID",
        "username": "Username",
    }

    strings_de = {
        "_cfg_cst_channel": "Die Kanal-ID, wo die Spenden gespeichert werden sollen.",
        "_cfg_cst_custom_message": "Die Nachricht, die an den Benutzer gesendet wird, nachdem das Abonnement hinzugefügt wurde. Benutze <br> für einen Zeilenumbruch.",
        "_cfg_cst_kickchannel": "Die Kanal-IDs, aus denen der Benutzer nach dem Abonnement gekickt werden soll.",
        "_cfg_cst_monthlyamount": "Die monatlichen Kosten des Abonnements.",
        "_cfg_cst_subscription_gift": "Das Geschenk, das an den Benutzer gesendet wird, nachdem das Abonnement hinzugefügt wurde. Wird an custom_message angehängt. Benutze <br> für einen Zeilenumbruch.",
        "_log_doc_kicked": "{} von {} gekickt.",
        "_log_doc_log_kicks": "Protokolliert die erfolgreichen Kicks aus den Chats.",
        "amount": "Betrag",
        "code": "Code",
        "date": "Datum",
        "donation_saved": "🎉 Spende gespeichert!",
        "dtype": "Spendentyp",
        "no_amount": "Kein Betrag gefunden.",
        "no_args": "Keine Argumente angegeben",
        "no_channel": "Kein Protokollkanal gesetzt.",
        "no_reply": "Du hast nicht auf eine Nachricht geantwortet.",
        "rank": "Rang",
        "total_amount": "<b><u>Gesamtbetrag der Spenden:</u></b>\n{}",
        "uname": "Name",
        "userid": "BenutzerID",
        "username": "Benutzername",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "logchannel",
                "None",
                lambda: self.strings("_cfg_cst_logchannel"),
                validator=loader.validators.Union(
                    loader.validators.TelegramID(),
                    loader.validators.NoneType(),
                ),
            ),
            loader.ConfigValue(
                "custom_message",
                ["Thank you very much for your donation! 🎉"],
                doc=lambda: self.strings("_cfg_cst_custom_message"),
                validator=loader.validators.Series(
                    validator=loader.validators.String()
                ),
            ),
            loader.ConfigValue(
                "kick_channel",
                doc=lambda: self.strings("_cfg_cst_kickchannel"),
                validator=loader.validators.Series(
                    validator=loader.validators.TelegramID()
                ),
            ),
            loader.ConfigValue(
                "log_kicks",
                True,
                doc=lambda: self.strings("_cfg_doc_log_kick"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "monthly_amount",
                10,
                doc=lambda: self.strings("_cfg_cst_monthlyamount"),
                validator=loader.validators.Integer(minimum=1)
            ),
            loader.ConfigValue(
                "subscription_gift",
                doc=lambda: self.strings("_cfg_cst_subscription_gift"),
                validator=loader.validators.Hidden(
                    validator=loader.validators.Series(
                        validator=loader.validators.String()
                    ),
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

    @staticmethod
    async def _is_member(
        chat: Union[Chat, int],
        user: Union[User, int],
        self_id: Union[None, int],
        message: Union[None, Message] = None,
    ):
        if chat != self_id:
            try:
                await message.client.get_permissions(chat, user)
                return True
            except UserNotParticipantError:
                return False

    async def cdonatorscmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def donamountcmd(self, message: Message):
        """
        Calculate the amount of donations.
        """
        if not self.config["logchannel"]:
            await utils.answer(message, self.strings("no_channel"))
            return
        amounts = await self._get_amounts(message, self.config["logchannel"])
        if amounts:
            await utils.answer(message, self.strings("total_amount").format(amounts))
        else:
            await utils.answer(message, self.strings("no_amount"))

    async def donsavecmd(self, message: Message):
        """
        Save donation. Reply to the user message!
        Pattern:
        .donsave <amount> <currency> <dtype> <rank> <code> | as reply!
        Example:
        .donsave 100 € amazon vip 123-123-123-123, 456-456-456-456 | as reply!
        """
        reply = await message.get_reply_message()
        if not self.config["logchannel"]:
            await utils.answer(message, self.strings("no_channel"))
            return
        if not reply:
            await utils.answer(message, self.strings("no_reply"))
            return
        user = await self._client.get_entity(reply.sender_id)
        if not user:
            await utils.answer(message, self.strings("no_user"))
            return
        args = utils.get_args_raw(message).lower()
        args = str(args).split()
        if not args:
            await utils.answer(message, self.strings("no_args"))
            return
        monthly_amount, today, uname, username, userid, amount, currency, dtype, rank, code = self._vars(user, args)

        string_join, string_kick = self._strings(today, uname, username, userid, amount, currency, dtype, rank, code)

        msg = await message.client.send_message(
            int(self.config["logchannel"]),
            string_join,
        )

        await message.client.send_message(
            int(self.config["logchannel"]),
            string_kick,
            schedule=(date.today() + timedelta(days=(int(amount)/monthly_amount*30))),
        )
        if self.config["custom_message"]:
            custom_msg = " ".join(self.config["custom_message"])
            if self.config["subscription_gift"]:
                custom_msg += " ".join(self.config["subscription_gift"])
            custom_msg = custom_msg.replace("<br>", "\n")
            await utils.answer(message, custom_msg)
        else:
            await utils.answer(message, self.strings("donation_saved"))
        await msg.react("👍")

    @staticmethod
    async def _get_amounts(message: Message, logchannel: int):
        amounts = ""
        amounts_euro = []
        amounts_usd = []
        amounts_gbp = []
        amounts_rub = []
        itermsg = message.client.iter_messages(entity=logchannel, limit=None)
        async for msg in itermsg:
            if (
                msg
                and isinstance(msg, Message)
                and "#join" in msg.raw_text.lower()
            ):
                msg_lines = msg.raw_text.splitlines()
                for lines in msg_lines:
                    if (
                        "€" in lines.lower()
                        or "$" in lines.lower()
                        or "£" in lines.lower()
                        or "₽" in lines.lower()
                    ):
                        for z in lines.split():
                            if "€" in z:
                                z = z.replace("€", "")
                                if z.isdigit():
                                    amounts_euro.append(int(z))
                            if "$" in z:
                                z = z.replace("$", "")
                                if z.isdigit():
                                    amounts_usd.append(int(z))
                            if "£" in z:
                                z = z.replace("£", "")
                                if z.isdigit():
                                    amounts_gbp.append(int(z))
                            if "₽" in z:
                                z = z.replace("₽", "")
                                if z.isdigit():
                                    amounts_rub.append(int(z))
        if amounts_euro:
            amounts += f"<code>{sum(amounts_euro)}€</code>\n"
        if amounts_usd:
            amounts += f"<code>{sum(amounts_usd)}$</code>\n"
        if amounts_gbp:
            amounts += f"<code>{sum(amounts_gbp)}£</code>\n"
        if amounts_rub:
            amounts += f"<code>{sum(amounts_rub)}₽</code>\n"
        return amounts

    def _vars(self, user, args):
        monthly_amount = self.config["monthly_amount"]
        today = date.today()
        uname = user.first_name
        if user.last_name:
            uname += f" {user.last_name}"
        username = f"@{user.username}" if user.username else ""
        userid = user.id
        amount = args[0]
        currency = args[1]
        dtype = args[2].capitalize()
        rank = args[3].upper()
        code = str(args[4:]).upper()
        return monthly_amount, today, uname, username, userid, amount, currency, dtype, rank, code

    def _strings(self, today, uname, username, userid, amount, currency, dtype, rank, code):
        string_join = ("#Join\n"
                       + f"#{self.strings('date')} {today}\n"
                       + f"#{self.strings('uname')} {uname}\n"
                       + f"#{self.strings('username')} {username}\n"
                       + f"#ID_{userid}\n"
                       + f"#{self.strings('dtype')} {dtype}\n"
                       + f"#{self.strings('amount')} {amount}{currency}\n"
                       + f"#{self.strings('rank')} {rank}\n"
                       + f"#{self.strings('code')} {code}\n")

        string_kick = ("#Kick\n"
                       + f"#{self.strings('date')} {today}\n"
                       + f"#{self.strings('uname')} {uname}\n"
                       + f"#{self.strings('username')} {username}\n"
                       + f"#ID_{userid}\n"
                       + f"#{self.strings('dtype')} {dtype}\n"
                       + f"#{self.strings('amount')} {amount}{currency}\n"
                       + f"#{self.strings('rank')} {rank}\n"
                       + f"#{self.strings('code')} {code}\n"
                       )
        return string_join, string_kick

    async def watcher(self, message: Message):
        if not isinstance(message, Message) or not self.config["logchannel"]:
            return
        if utils.get_chat_id(message) != self.config["logchannel"]:
            return
        if "#kick" not in message.raw_text.lower():
            return
        msg_lines = message.raw_text.splitlines()
        for text in msg_lines:
            if "#ID_" in text:
                userid = int(text.replace("#ID_", ""))
        kchannels = self.config["kick_channel"]
        for kchannel in kchannels:
            if await self._is_member(kchannel, userid, self._tg_id, message):
                await message.client.kick_participant(
                    kchannel,
                    userid,
                )
                logger.info(self.strings("_log_doc_kicked").format(userid, kchannel))
        await message.react("👍")


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
