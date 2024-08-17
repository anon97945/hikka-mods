__version__ = (2, 1, 1)


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
# 🔒 Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# Original author: @mishase
# API author: @mishase

# requires: requests Pillow cryptg

import logging
import contextlib
import hashlib
import json
import requests
import io
import PIL
from telethon import utils
from telethon.utils import get_display_name
from telethon.tl.types import (
    Message,
    MessageEntityBold,
    MessageEntityItalic,
    MessageEntityMention,
    MessageEntityTextUrl,
    MessageEntityCode,
    MessageEntityMentionName,
    MessageEntityHashtag,
    MessageEntityCashtag,
    MessageEntityBotCommand,
    MessageEntityUrl,
    MessageEntityStrike,
    MessageEntityUnderline,
    MessageEntityPhone,
    ChatPhotoEmpty,
    MessageMediaPhoto,
    MessageMediaDocument,
    MessageMediaWebPage,
    User,
    PeerUser,
    PeerBlocked,
    PeerChannel,
    PeerChat,
    DocumentAttributeSticker,
    ChannelParticipantsAdmins,
    ChannelParticipantCreator,
)
from .. import loader, utils

logger = logging.getLogger(__name__)

null = None
false = False
true = True

PIL.Image.MAX_IMAGE_PIXELS = null


class dict(dict):
    def __setattr__(self, attr, value):
        self[attr] = value


@loader.tds
class ApodiktumQuotesMod(loader.Module):
    """Quote a message using Mishase Quotes API"""

    strings = {
        "name": "Apo-Quotes",
        "developer": "@anon97945",
        "_cfg_msg_limit": "Messages limit",
        "_cfg_max_width": "Max width (px)",
        "_cfg_scale_factor": "Scale factor",
        "_cfg_square_avatar": "Square avatar",
        "_cfg_text_color": "Text color",
        "_cfg_reply_line_color": "Reply line color",
        "_cfg_admin_title_color": "Admin title color",
        "_cfg_message_border_radius": "Message radius (px)",
        "_cfg_reply_thumb_border_radius": "Reply thumbnail radius (px)",
        "_cfg_picture_border_radius": "Picture radius (px)",
        "_cfg_background_color": "Background color",
    }

    strings_de = {}

    strings_ru = {}

    all_strings = {
        "strings": strings,
        "strings_en": strings,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    changes = {}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "QUOTE_MESSAGES_LIMIT",
                50,
                doc=lambda: self.strings("_cfg_msg_limit"),
                validator=loader.validators.Integer(),
            ),
            # "QUOTE_MESSAGES_LIMIT",
            # 50,
            # "Messages limit",
            loader.ConfigValue(
                "MAX_WIDTH",
                384,
                doc=lambda: self.strings("_cfg_max_width"),
                validator=loader.validators.Integer(),
            ),
            # "MAX_WIDTH",
            # 384,
            # "Max width (px)",
            loader.ConfigValue(
                "SCALE_FACTOR",
                5,
                doc=lambda: self.strings("_cfg_scale_factor"),
                validator=loader.validators.Integer(),
            ),
            # "SCALE_FACTOR",
            # 5,
            # "Scale factor",
            loader.ConfigValue(
                "SQUARE_AVATAR",
                False,
                doc=lambda: self.strings("_cfg_square_avatar"),
                validator=loader.validators.Boolean(),
            ),
            # "SQUARE_AVATAR",
            # false,
            # "Square avatar",
            loader.ConfigValue(
                "TEXT_COLOR",
                "white",
                doc=lambda: self.strings("_cfg_text_color"),
                validator=loader.validators.String(),
            ),
            # "TEXT_COLOR",
            # "white",
            # "Text color",
            loader.ConfigValue(
                "REPLY_LINE_COLOR",
                "white",
                doc=lambda: self.strings("_cfg_reply_line_color"),
                validator=loader.validators.String(),
            ),
            # "REPLY_LINE_COLOR",
            # "white",
            # "Reply line color",
            loader.ConfigValue(
                "REPLY_THUMB_BORDER_RADIUS",
                2,
                doc=lambda: self.strings("_cfg_reply_thumb_border_radius"),
                validator=loader.validators.Integer(),
            ),
            # "REPLY_THUMB_BORDER_RADIUS",
            # 2,
            # "Reply thumbnail radius (px)",
            loader.ConfigValue(
                "ADMINTITLE_COLOR",
                "#969ba0",
                doc=lambda: self.strings("_cfg_admin_title_color"),
                validator=loader.validators.String(),
            ),
            # "ADMINTITLE_COLOR",
            # "#969ba0",
            # "Admin title color",
            loader.ConfigValue(
                "MESSAGE_BORDER_RADIUS",
                10,
                doc=lambda: self.strings("_cfg_message_border_radius"),
                validator=loader.validators.Integer(),
            ),
            # "MESSAGE_BORDER_RADIUS",
            # 10,
            # "Message radius (px)",
            loader.ConfigValue(
                "PICTURE_BORDER_RADIUS",
                8,
                doc=lambda: self.strings("_cfg_picture_border_radius"),
                validator=loader.validators.Integer(),
            ),
            # "PICTURE_BORDER_RADIUS",
            # 8,
            # "Picture radius (px)",
            loader.ConfigValue(
                "BACKGROUND_COLOR",
                "#162330",
                doc=lambda: self.strings("_cfg_background_color"),
                validator=loader.validators.String(),
            ),
            # "BACKGROUND_COLOR",
            # "#162330",
            # "Background color",
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

    async def cquotescmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def quotecmd(self, msg):
        """Quote a message. Args: .<count> .file"""
        args = utils.get_args_raw(msg)
        reply = await msg.get_reply_message()

        if not reply:
            return await msg.edit("No reply message")

        if not msg.out:
            msg = await msg.reply("_")

        count = 1
        forceDocument = false

        if args:
            args = args.split()
            forceDocument = "file" in args
            with contextlib.suppress(StopIteration):
                count = next(int(arg) for arg in args if arg.isdigit())
                count = max(1, min(self.config["QUOTE_MESSAGES_LIMIT"], count))
        messagePacker = MessagePacker(self._client)

        if count == 1:
            await msg.edit("<b>Processing...</b>")
            await messagePacker.add(reply)
        if count > 1:
            it = self._client.iter_messages(
                reply.peer_id,
                offset_id=reply.id,
                reverse=true,
                add_offset=1,
                limit=count,
            )

            i = 1
            async for message in it:
                await msg.edit(f"<b>Processing {i}/{count}</b>")
                i += 1
                await messagePacker.add(message)

        messages = messagePacker.messages

        if not messages:
            return await msg.edit("No messages to quote")

        files = [("files", f) for f in messagePacker.files.values()]
        if not files:
            files.append(("files", bytearray()))

        await msg.edit("<b>API Processing...</b>")

        resp = await utils.run_sync(
            requests.post,
            "https://quotes.mishase.dev/create",
            data={
                "data": json.dumps(
                    {
                        "messages": messages,
                        "maxWidth": self.config["MAX_WIDTH"],
                        "scaleFactor": self.config["SCALE_FACTOR"],
                        "squareAvatar": self.config["SQUARE_AVATAR"],
                        "textColor": self.config["TEXT_COLOR"],
                        "replyLineColor": self.config["REPLY_LINE_COLOR"],
                        "adminTitleColor": self.config["ADMINTITLE_COLOR"],
                        "messageBorderRadius": self.config["MESSAGE_BORDER_RADIUS"],
                        "replyThumbnailBorderRadius": self.config[
                            "REPLY_THUMB_BORDER_RADIUS"
                        ],
                        "pictureBorderRadius": self.config["PICTURE_BORDER_RADIUS"],
                        "backgroundColor": self.config["BACKGROUND_COLOR"],
                    }
                ),
                "moduleBuild": null,
            },
            files=files,
            timeout=99,
        )

        if resp.status_code == 418:
            logger.error("API Error: %s", resp.text)
            msg.delete()
            return

        await msg.edit("<b>Sending...</b>")

        image = io.BytesIO()
        image.name = "quote.webp"

        PIL.Image.open(io.BytesIO(resp.content)).save(image, "WEBP")
        image.seek(0)
        await self._client.send_message(
            msg.peer_id,
            file=image,
            force_document=forceDocument,
            reply_to=utils.get_topic(msg),
        )
        await msg.delete()

    async def fquotecmd(self, msg):
        """Fake message quote. Args: @<username>/<id>/<reply> <text>"""
        args = utils.get_args_raw(msg)
        reply = await msg.get_reply_message()
        splitArgs = args.split(maxsplit=1)
        if len(splitArgs) == 2 and (
            splitArgs[0].startswith("@") or splitArgs[0].isdigit()
        ):
            user = (
                splitArgs[0][1:] if splitArgs[0].startswith("@") else int(splitArgs[0])
            )
            text = splitArgs[1]
        elif reply:
            user = reply.sender_id
            text = args
        else:
            return await msg.edit("Incorrect args")

        try:
            uid = (await self._client.get_entity(user)).id
        except Exception:
            return await msg.edit("User not found")

        async def getMessage():
            return Message(0, uid, message=text)

        msg.message = ""
        msg.get_reply_message = getMessage

        await self.quotecmd(msg)


class MessagePacker:
    def __init__(self, client):
        self.files = {}
        self.messages = []
        self._client = client

    async def add(self, msg):
        packed = await self.packMessage(msg)
        if packed:
            self.messages.append(packed)

    async def packMessage(self, msg):
        obj = {}

        if text := msg.message:
            obj["text"] = text

        if entities := MessagePacker.encodeEntities(msg.entities or []):
            obj["entities"] = entities

        if media := msg.media:
            file = await self.downloadMedia(media)
            if file:
                obj["picture"] = {"file": file}

        if "text" not in obj and "picture" not in obj:
            return null

        obj["author"] = await self.encodeAuthor(msg)

        reply = await msg.get_reply_message()
        if reply:
            obj["reply"] = await self.encodeReply(reply)

        return obj

    @staticmethod
    def encodeEntities(entities):
        encEntities = []
        for entity in entities:
            if entityType := MessagePacker.getEntityType(entity):
                encEntities.append(
                    {
                        "type": entityType,
                        "offset": entity.offset,
                        "length": entity.length,
                    }
                )
        return encEntities

    @staticmethod
    def getEntityType(entity):
        t = type(entity)
        if t is MessageEntityBold:
            return "bold"
        if t is MessageEntityItalic:
            return "italic"
        if t in [MessageEntityUrl, MessageEntityPhone]:
            return "url"
        if t is MessageEntityCode:
            return "monospace"
        if t is MessageEntityStrike:
            return "strikethrough"
        if t is MessageEntityUnderline:
            return "underline"
        if t in [
            MessageEntityMention,
            MessageEntityTextUrl,
            MessageEntityMentionName,
            MessageEntityHashtag,
            MessageEntityCashtag,
            MessageEntityBotCommand,
        ]:
            return "bluetext"
        return null

    async def downloadMedia(self, inMedia, thumb=null):
        media = MessagePacker.getMedia(inMedia)
        if not media:
            return null
        mid = str(media.id)
        if thumb:
            mid += f".{str(thumb)}"
        if mid not in self.files:
            try:
                mime = media.mime_type
            except AttributeError:
                mime = "image/jpg"
            dl = await self._client.download_media(media, bytes, thumb=thumb)
            self.files[mid] = (str(len(self.files)), dl, mime)
        return self.files[mid][0]

    @staticmethod
    def getMedia(media):
        t = type(media)
        if t is MessageMediaPhoto:
            return media.photo
        if t is MessageMediaDocument:
            for attribute in media.document.attributes:
                if isinstance(attribute, DocumentAttributeSticker):
                    return media.document
        elif t is MessageMediaWebPage:
            if media.webpage.type == "photo":
                return media.webpage.photo
        return null

    async def downloadProfilePicture(self, entity):
        media = entity.photo
        if not media or isinstance(media, ChatPhotoEmpty):
            return null
        mid = str(media.photo_id)
        if mid not in self.files:
            dl = await self._client.download_profile_photo(entity, bytes)
            self.files[mid] = (str(len(self.files)), dl, "image/jpg")
        return self.files[mid][0]

    async def encodeAuthor(self, msg):
        uid, name, picture, adminTitle = await self.getAuthor(msg)

        obj = {"id": uid, "name": name}
        if picture:
            obj["picture"] = {"file": picture}
        if adminTitle:
            obj["adminTitle"] = adminTitle

        return obj

    async def getAuthor(self, msg, full=true):
        uid = null
        name = null
        picture = null
        adminTitle = null

        chat = msg.peer_id
        peer = msg.from_id or chat
        if fwd := msg.fwd_from:
            peer = fwd.from_id
            name = fwd.post_author or fwd.from_name

        t = type(peer)
        if t is int:
            uid = peer
        elif t is PeerUser:
            uid = peer.user_id
        elif t is PeerChannel:
            uid = peer.channel_id
        elif t is PeerChat:
            uid = peer.chat_id
        elif t is PeerBlocked:
            uid = peer.peer_id
        elif not peer:
            uid = int(hashlib.shake_256(name.encode("utf-8")).hexdigest(6), 16)

        if not name:
            entity = null
            try:
                entity = await self._client.get_entity(peer)
            except Exception:
                entity = await msg.get_chat()

            if isinstance(entity, User) and entity.deleted:
                name = "Deleted Account"
            else:
                name = get_display_name(entity)

            if full:
                picture = await self.downloadProfilePicture(entity)

                if isinstance(chat, (PeerChannel, PeerChat)):
                    admins = await self._client.get_participants(
                        chat, filter=ChannelParticipantsAdmins
                    )
                    for admin in admins:
                        participant = admin.participant
                        if participant.user_id == uid:
                            try:
                                adminTitle = participant.rank
                            except AttributeError:
                                adminTitle = null
                            if not adminTitle:
                                if isinstance(participant, ChannelParticipantCreator):
                                    adminTitle = "owner"
                                else:
                                    adminTitle = "admin"
                            break

        return uid, name, picture, adminTitle

    async def encodeReply(self, reply):
        obj = {}

        if text := reply.message:
            obj["text"] = text
        elif media := reply.media:
            t = type(media)
            obj.text = "📷 Photo" if t is MessageMediaPhoto else "💾 File"
        name = (await self.getAuthor(reply, full=false))[1]

        obj["author"] = name

        if media := reply.media:
            file = await self.downloadMedia(media, -1)
            if file:
                obj["thumbnail"] = {"file": file}

        return obj
