__version__ = (0, 1, 71)


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

# scope: libsndfile1 gcc ffmpeg rubberband-cli
# scope: hikka_only
# scope: hikka_min 1.1.28

# requires: gtts pydub soundfile pyrubberband numpy AudioSegment wave

import logging
import os
import soundfile
import pyrubberband

from gtts import gTTS
from io import BytesIO
from .. import loader, utils
from subprocess import Popen, PIPE
from pydub import AudioSegment, effects
from telethon.tl.types import Message


logger = logging.getLogger(__name__)


async def audionormalizer(bytes_io_file, fn, fe):
    # return bytes_io_file, fn, fe
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    rawsound = AudioSegment.from_file(bytes_io_file, "wav")
    normalizedsound = effects.normalize(rawsound)
    bytes_io_file.seek(0)
    normalizedsound.export(bytes_io_file, format="wav")
    bytes_io_file.name = f"{fn}.wav"
    fn, fe = os.path.splitext(bytes_io_file.name)
    return bytes_io_file, fn, fe


async def audiohandler(bytes_io_file, fn, fe):
    # return bytes_io_file, fn, fe
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    content = bytes_io_file.getvalue()
    cmd = ['ffmpeg', '-y', '-i', 'pipe:', '-acodec', 'pcm_s16le', '-f', 'wav', '-ac', '1', 'pipe:']
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=-1)
    out, _ = p.communicate(input=content)
    p.stdin.close()
    bytes_io_file.name = f"{fn}.wav"
    fn, fe = os.path.splitext(bytes_io_file.name)
    return BytesIO(out), fn, fe if out.startswith(b'RIFF\xff\xff\xff') else None


async def makewaves(bytes_io_file, fn, fe):
    # return bytes_io_file, fn, fe
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    content = bytes_io_file.getvalue()
    cmd = ['ffmpeg', '-y', '-i', 'pipe:', '-c:a', 'libopus', '-f', 'opus', '-ac', '2', 'pipe:']
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=-1)
    out, _ = p.communicate(input=content)
    p.stdin.close()
    bytes_io_file.name = f"{fn}.ogg"
    fn, fe = os.path.splitext(bytes_io_file.name)
    return BytesIO(out), fn, fe


def represents_speed(s):
    try:
        float(s)
        return 0.25 <= float(s) <= 3
    except ValueError:
        return False


async def speedup(bytes_io_file, fn, fe, speed):
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    y, sr = soundfile.read(bytes_io_file)
    y_stretch = pyrubberband.time_stretch(y, sr, speed)
    bytes_io_file.seek(0)
    soundfile.write(bytes_io_file, y_stretch, sr, format='wav')
    bytes_io_file.seek(0)
    bytes_io_file.name = f"{fn}.wav"
    return bytes_io_file, fn, fe


@loader.tds
class ApodiktumTTSMod(loader.Module):
    strings = {
        "name": "Apo TextToSpeech",
        "developer": "@anon97945",
        "_cfg_tts_lang": "Set your language code for the TTS here.",
        "_cfg_tts_speed": "Set the desired speech speed.",
        "needspeed": "You need to provide a speed value between 0.25 and 3.0.",
        "needvoice": "<b>[TTS]</b> This command needs a voicemessage.",
        "no_reply": "<b>[TTS]</b> You need to reply to a voicemessage.",
        "no_speed": "<b>[TTS]</b> Your input was an unsupported speed value.",
        "processing": "<b>[TTS]</b> Message is being processed ...",
        "tts_needs_text": "<b>[TTS]</b> I need text to convert to speech!",
    }

    strings_de = {
        "_cfg_tts_lang": "Stellen Sie hier Ihren Sprachcode für TTS ein.",
        "_cfg_tts_speed": "Stellen Sie die gewünschte Sprechgeschwindigkeit ein.",
        "_cmd_doc_ctts": "Dadurch wird die Konfiguration für das Modul geöffnet.",
        "needspeed": "Sie müssen einen Geschwindigkeitswert zwischen 0.25 und 3.0 angeben.",
        "needvoice": "<b>[TTS]</b> Dieser Befehl benötigt eine Sprachnachricht.",
        "no_reply": "<b>[TTS]</b> Sie müssen auf eine Sprachnachricht antworten.",
        "no_speed": "<b>[TTS]</b> Ihre Eingabe war ein nicht unterstützter Geschwindigkeitswert.",
        "processing": "<b>[TTS]</b> Nachricht wird verarbeitet ...",
        "tts_needs_text": "<b>[TTS]</b> Ich brauche Text, um ihn in Sprache umzuwandeln!",
    }

    strings_ru = {
        "_cfg_tts_lang": "Установите ваш код страны для TTS здесь.",
        "_cfg_tts_speed": "Установите желаемую скорость речи.",
        "_cmd_doc_ctts": "Это откроет конфиг для модуля.",
        "needspeed": "Вам нужно предоставить значение скорости между 0.25 и 3.0",
        "needvoice": "<b>[TTS]</b> Этой команде нужно голосовое сообщение.",
        "no_reply": "<b>[TTS]</b> Вам нужно сделать реплай на голосовое сообщение.",
        "no_speed": "<b>[TTS]</b> Ваш ввод является неподдерживаемым значением скорости.",
        "processing": "<b>[TTS]</b> Сообщение обрабатывается...",
        "tts_needs_text": "<b>[TTS]</b> Мне нужен текст для преобразования в речь!",
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "tts_lang",
                "en",
                doc=lambda: self.strings("_cfg_tts_lang"),
            ),
            loader.ConfigValue(
                "tts_speed",
                "1",
                doc=lambda: self.strings("_cfg_tts_speed"),
                validator=loader.validators.Float(minimum=0.25, maximum=3),
            ),
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

    async def cttscmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def ttscmd(self, message: Message):
        """Convert text to speech with Google APIs"""
        speed = self.config["tts_speed"]
        text = utils.get_args_raw(message.message)
        if len(text) == 0:
            if message.is_reply:
                text = (await message.get_reply_message()).message
            else:
                return await utils.answer(message, self.strings("tts_needs_text"))
        message = await utils.answer(message, self.strings("processing"))
        tts = await utils.run_sync(gTTS, text, lang=self.config["tts_lang"])
        voice = BytesIO()
        await utils.run_sync(tts.write_to_fp, voice)
        voice.seek(0)
        voice.name = "voice.mp3"
        fn, fe = os.path.splitext(voice.name)
        voice, fn, fe = await audiohandler(voice, fn, fe)
        voice.seek(0)
        voice, fn, fe = await speedup(voice, fn, fe, float(speed))
        voice.seek(0)
        voice, fn, fe = await audionormalizer(voice, fn, fe)
        voice.seek(0)
        voice, fn, fe = await makewaves(voice, fn, fe)
        voice.seek(0)
        voice.name = fn + fe
        await utils.answer(message, voice, voice_note=True)
        if message.out:
            await message.delete()

    async def speedvccmd(self, message: Message):
        """Speed up voice by x"""
        speed = utils.get_args_raw(message)
        if not message.is_reply:
            return await utils.answer(message, self.strings("no_reply"))
        replymsg = await message.get_reply_message()
        if not replymsg.voice:
            message = await utils.answer(message, self.strings("needvoice"))
            return
        if len(speed) == 0:
            return await utils.answer(message, self.strings("needspeed"))
        if not represents_speed(speed):
            return await utils.answer(message, self.strings("no_speed"))
        message = await utils.answer(message, self.strings("processing"))
        ext = replymsg.file.ext
        voice = BytesIO()
        voice.name = replymsg.file.name
        await replymsg.client.download_file(replymsg, voice)
        voice.name = f"voice{ext}"
        fn, fe = os.path.splitext(voice.name)
        voice.seek(0)
        voice, fn, fe = await audiohandler(voice, fn, fe)
        voice.seek(0)
        voice, fn, fe = await speedup(voice, fn, fe, float(speed))
        voice.seek(0)
        voice, fn, fe = await audionormalizer(voice, fn, fe)
        voice.seek(0)
        voice, fn, fe = await makewaves(voice, fn, fe)
        voice.seek(0)
        voice.name = fn + fe
        await utils.answer(message, voice, voice_note=True)
        if message.out:
            await message.delete()
