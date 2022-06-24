__version__ = (0, 0, 3)

# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @apodiktum_modules

# scope: hikka_only
# scope: hikka_min 1.1.28


from telethon.errors import UserNotParticipantError
from telethon.tl.types import Message, Chat, User
from datetime import timedelta, date
from typing import Union

import logging
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
        "_cfg_cst_channel": "The Channel ID where the donations should be saved.",
        "_cfg_cst_custom_message": "The message send to the user after the subscription is added.",
        "_cfg_cst_kickchannel": "The channel ids to kick the user from after the subscription",
        "_cfg_cst_monthlyamount": "The monthly cost of the subscription.",
        "_cfg_doc_log_kick": "Logs successful kicks from the chats.",
        "_log_doc_kicked": "Kicked {} from {}.",
        "total_amount": "<b><u>Total amount of donations:</u></b>\n{}",
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
        "uname": "Name",
        "userid": "UserID",
        "username": "Username",
    }

    strings_de = {
        "_cfg_cst_channel": "Die Kanal-ID, wo die Spenden gespeichert werden sollen.",
        "_cfg_cst_custom_message": "Die Nachricht, die an den Benutzer gesendet wird, nachdem das Abonnement hinzugefügt wurde.",
        "_cfg_cst_kickchannel": "Die Kanal-IDs, aus denen der Benutzer nach dem Abonnement gekickt werden soll.",
        "_cfg_cst_monthlyamount": "Die monatlichen Kosten des Abonnements.",
        "_log_doc_kicked": "{} von {} gekickt.",
        "_log_doc_log_kicks": "Protokolliert die erfolgreichen Kicks aus den Chats.",
        "total_amount": "<b><u>Gesamtbetrag der Spenden:</u></b>\n{}",
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
                "kick_channel",
                doc=lambda: self.strings("_cfg_cst_kickchannel"),
                validator=loader.validators.Series(
                    validator=loader.validators.TelegramID()
                ),
            ),
            loader.ConfigValue(
                "monthly_amount",
                10,
                doc=lambda: self.strings("_cfg_cst_monthlyamount"),
                validator=loader.validators.Integer(minimum=1)
            ),
            loader.ConfigValue(
                "custom_message",
                doc=lambda: self.strings("_cfg_cst_custom_message"),
            ),
            loader.ConfigValue(
                "custom_message",
                doc=lambda: self.strings("_cfg_cst_custom_message"),
            ),
            loader.ConfigValue(
                "log_kicks",
                True,
                doc=lambda: self.strings("_cfg_doc_log_kick"),
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

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
        amounts = ""
        amounts_euro = []
        amounts_usd = []
        amounts_gbp = []
        amounts_rub = []
        itermsg = message.client.iter_messages(entity=int(self.config[]), limit=None)
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
                       + f"#{self.strings('code')} {code}\n")

        msg = await message.client.send_message(
            int(self.config["logchannel"]),
            string_join,
        )

        await message.client.send_message(
            int(self.config["log"]),
            string_kick,
            schedule=(date.today() + timedelta(days=(int(amount)/monthly_amount*30))),
        )
        if self.config["custom_message"]:
            await utils.answer(message, self.config["custom_message"])
        else:
            await utils.answer(message, self.strings("donation_saved"))
        await msg.react("👍")

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
