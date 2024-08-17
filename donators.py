__version__ = (0, 0, 31)


# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#           © Copyright 2024
#
#        developed by @anon97945
#
#     https://t.me/apodiktum_modules
#      https://github.com/anon97945
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/gpl-3.0.html

# meta developer: @apodiktum_modules
# meta banner: https://t.me/apodiktum_dumpster/11
# meta pic: https://t.me/apodiktum_dumpster/13

# scope: hikka_only
# scope: hikka_min 1.3.3

import logging
from datetime import date, timedelta

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ApodiktumDonatorsMod(loader.Module):
    """
    Handle donations in a given channel and kick them after the period of time.
    """

    strings = {
        "name": "Apo-Donators",
        "developer": "@anon97945",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_cst_channel": "The Channel ID where the donations should be saved.",
        "_cfg_cst_custom_message": (
            "The message send to the user after the subscription is added. Use"
            " <br> for new line."
        ),
        "_cfg_cst_kickchannel": (
            "The channel ids to kick the user from after the subscription."
        ),
        "_cfg_cst_monthlyamount": "The monthly cost of the subscription.",
        "_cfg_cst_subscription_gift": (
            "The gift to send to the user after the subscription. Will be"
            " attached to custom_message. Use <br> for new line."
        ),
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

    strings_en = {}

    strings_de = {
        "_cfg_cst_channel": "Die Kanal-ID, wo die Spenden gespeichert werden sollen.",
        "_cfg_cst_custom_message": (
            "Die Nachricht, die an den Benutzer gesendet wird, nachdem das"
            " Abonnement hinzugefügt wurde. Benutze <br> für einen"
            " Zeilenumbruch."
        ),
        "_cfg_cst_kickchannel": (
            "Die Kanal-IDs, aus denen der Benutzer nach dem Abonnement gekickt"
            " werden soll."
        ),
        "_cfg_cst_monthlyamount": "Die monatlichen Kosten des Abonnements.",
        "_cfg_cst_subscription_gift": (
            "Das Geschenk, das an den Benutzer gesendet wird, nachdem das"
            " Abonnement hinzugefügt wurde. Wird an custom_message angehängt."
            " Benutze <br> für einen Zeilenumbruch."
        ),
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

    strings_ru = {}

    all_strings = {
        "strings": strings,
        "strings_en": strings,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    changes = {
        "migration1": {
            "name": {
                "old": "Apo Donators",
                "new": "Apo-Donators",
            },
        },
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
                validator=loader.validators.Integer(minimum=1),
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
        )

    async def client_ready(self):
        self.apo_lib = await self.import_lib(
            "https://raw.githubusercontent.com/anon97945/hikka-libs/master/apodiktum_library.py",
            suspend_on_error=True,
        )
        await self.apo_lib.migrator.auto_migrate_handler(
            self.__class__.__name__,
            self.strings("name"),
            self.changes,
            self.config["auto_migrate"],
        )

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
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_channel", self.all_strings, message),
            )
            return
        amounts = await self._get_amounts(message, self.config["logchannel"])
        if amounts:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str(
                    "total_amount", self.all_strings, message
                ).format(amounts),
            )
        else:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_amount", self.all_strings, message),
            )

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
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_channel", self.all_strings, message),
            )
            return
        if not reply:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_reply", self.all_strings, message),
            )
            return
        user = await reply.get_sender()
        if not user:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_user", self.all_strings, message),
            )
            return
        args = utils.get_args_raw(message).lower()
        args = str(args).split()
        if not args:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_args", self.all_strings, message),
            )
            return
        (
            monthly_amount,
            today,
            uname,
            username,
            userid,
            amount,
            currency,
            dtype,
            rank,
            code,
        ) = self._vars(user, args)

        string_join, string_kick = self._jk_strings(
            today, uname, username, userid, amount, currency, dtype, rank, code
        )

        msg = await message.client.send_message(
            int(self.config["logchannel"]),
            string_join,
        )

        await message.client.send_message(
            int(self.config["logchannel"]),
            string_kick,
            schedule=(
                date.today() + timedelta(days=int(amount) / monthly_amount * 30)
            ),
        )
        if self.config["custom_message"]:
            custom_msg = " ".join(self.config["custom_message"])
            if self.config["subscription_gift"]:
                custom_msg += " ".join(self.config["subscription_gift"])
            custom_msg = custom_msg.replace("<br>", "\n")
            await utils.answer(message, custom_msg)
        else:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("donation_saved", self.all_strings, message),
            )
        await msg.react("👍")

    async def _get_amounts(self, message: Message, logchannel: int):
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
                and "#join" in self.apo_lib.utils.raw_text(msg).lower()
            ):
                msg_lines = self.apo_lib.utils.raw_text(msg).splitlines()
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
        return (
            monthly_amount,
            today,
            uname,
            username,
            userid,
            amount,
            currency,
            dtype,
            rank,
            code,
        )

    def _jk_strings(
        self,
        today,
        uname,
        username,
        userid,
        amount,
        currency,
        dtype,
        rank,
        code,
    ):
        string_join = (
            "#Join\n"
            + f"#{self.strings('date')} {today}\n"
            + f"#{self.strings('uname')} {uname}\n"
            + f"#{self.strings('username')} {username}\n"
            + f"#ID_{userid}\n"
            + f"#{self.strings('dtype')} {dtype}\n"
            + f"#{self.strings('amount')} {amount}{currency}\n"
            + f"#{self.strings('rank')} {rank}\n"
            + f"#{self.strings('code')} {code}\n"
        )

        string_kick = (
            "#Kick\n"
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

    @loader.watcher("only_messages")
    async def watcher(self, message: Message):
        if (
            not self.config["logchannel"]
            or utils.get_chat_id(message) != self.config["logchannel"]
            or "#kick" not in self.apo_lib.utils.raw_text(message).lower()
        ):
            return

        msg_lines = self.apo_lib.utils.raw_text(message).splitlines()
        for text in msg_lines:
            if "#ID_" in text:
                userid = int(text.replace("#ID_", ""))
        kchannels = self.config["kick_channel"]
        for kchannel in kchannels:
            if await self.apo_lib.utils.is_member(kchannel, userid):
                await message.client.kick_participant(
                    kchannel,
                    userid,
                )
                self.apo_lib.utils.log(
                    logging.INFO,
                    __name__,
                    self.strings("_log_doc_kicked").format(userid, kchannel),
                )
        await message.react("👍")
