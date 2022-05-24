__version__ = (0, 0, 43)


# ▄▀█ █▄░█ █▀█ █▄░█ █▀▄ ▄▀█ █▀▄▀█ █░█ █▀
# █▀█ █░▀█ █▄█ █░▀█ █▄▀ █▀█ █░▀░█ █▄█ ▄█
#
#              © Copyright 2022
#
#          https://t.me/apodiktum_modules
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @anon97945
# scope: hikka_only
# requires: numpy scipy noisereduce soundfile pyrubberband

import logging
import numpy as np
import scipy.io.wavfile as wavfile
import os
import subprocess
import noisereduce as nr
import soundfile
import pyrubberband
import io

from telethon.tl.types import Message
from io import BytesIO
from pydub import AudioSegment, effects
from .. import loader, utils

logger = logging.getLogger(__name__)


async def getchattype(message):
    chattype = ""
    if message.is_group:
        chattype = "supergroup" if message.is_channel else "smallgroup"
    elif message.is_channel:
        chattype = "channel"
    elif message.is_private:
        chattype = "private"
    return chattype


def represents_nr(nr_lvl):
    try:
        float(nr_lvl)
        return 0.01 <= float(nr_lvl) <= 1
    except ValueError:
        return False


def represents_pitch(pitch_lvl):
    try:
        float(pitch_lvl)
        return -18 <= float(pitch_lvl) <= 18
    except ValueError:
        return False


def represents_speed(s):
    try:
        float(s)
        return 0.25 <= float(s) <= 3
    except ValueError:
        return False


async def audiohandler(bytes_io_file, fn, fe, new_fe, ac, codec):
    # return bytes_io_file, fn, fe, new_fe
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    out = fn + new_fe
    if fe != new_fe:
        new_fe_nodot = new_fe[1:]
        with open(fn + fe, "wb") as f:
            f.write(bytes_io_file.getbuffer())
        bytes_io_file.seek(0)
        subprocess.call([
                        "ffmpeg",
                        "-y",
                        "-i", fn + fe,
                        "-c:a", codec,
                        "-f", new_fe_nodot,
                        "-ar", "48000",
                        "-b:a", "320k",
                        "-ac", ac,
                        out,
                        ])
        with open(out, "rb") as f:
            bytes_io_file = BytesIO(f.read())
        bytes_io_file.seek(0)
        _, new_fe = os.path.splitext(out)
    if os.path.exists(out):
        os.remove(out)
    if os.path.exists(fn + fe):
        os.remove(fn + fe)
    return bytes_io_file, fn, new_fe


async def audiopitcher(bytes_io_file, fn, fe, pitch_lvl):
    # return bytes_io_file, fn, fe, pitch_lvl
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    format_ext = fe[1:]
    y, sr = soundfile.read(bytes_io_file)
    y_shift = pyrubberband.pitch_shift(y, sr, pitch_lvl)
    bytes_io_file.seek(0)
    soundfile.write(bytes_io_file, y_shift, sr, format=format_ext)
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    return bytes_io_file, fn, fe


async def audiodenoiser(bytes_io_file, fn, fe, nr_lvl):
    # return bytes_io_file, fn, fe, nr_lvl
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    rate, data = wavfile.read(bytes_io_file)
    reduced_noise = nr.reduce_noise(y=data, sr=rate, prop_decrease=nr_lvl, stationary=False)
    wavfile.write(bytes_io_file, rate, reduced_noise)
    fn, fe = os.path.splitext(bytes_io_file.name)
    fn, fe = os.path.splitext(bytes_io_file.name)
    return bytes_io_file, fn, fe


async def audionormalizer(bytes_io_file, fn, fe, db):
    # return bytes_io_file, fn, fe
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    format_ext = fe[1:]
    rawsound = AudioSegment.from_file(bytes_io_file, format_ext)
    normalizedsound = effects.normalize(rawsound)
    normalizedsound = normalizedsound + db
    bytes_io_file.seek(0)
    normalizedsound.export(bytes_io_file, format=format_ext)
    bytes_io_file.name = fn + fe
    fn, fe = os.path.splitext(bytes_io_file.name)
    return bytes_io_file, fn, fe


async def audiospeedup(bytes_io_file, fn, fe, speed):
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    format_ext = fe[1:]
    y, sr = soundfile.read(bytes_io_file)
    y_stretch = pyrubberband.time_stretch(y, sr, speed)
    bytes_io_file.seek(0)
    soundfile.write(bytes_io_file, y_stretch, sr, format=format_ext)
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    return bytes_io_file, fn, fe


async def dalekvoice(bytes_io_file, fn, fe):
    # return bytes_io_file, fn, fe
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    format_ext = fe[1:]

    sound = AudioSegment.from_wav(bytes_io_file)
    sound = sound.set_channels(2)
    sound.export(bytes_io_file, format=format_ext)
    bytes_io_file.seek(0)
    VB = 0.2
    VL = 0.4
    H = 4
    LOOKUP_SAMPLES = 1024
    MOD_F = 50

    def diode_lookup(n_samples):
        result = np.zeros((n_samples,))
        for i in range(n_samples):
            v = float(i - float(n_samples) / 2) / (n_samples / 2)
            v = abs(v)
            if v < VB:
                result[i] = 0
            elif VB < v <= VL:
                result[i] = H * ((v - VB)**2) / (2 * VL - 2 * VB)
            else:
                result[i] = H * v - H * VL + (H * (VL - VB)**2) / (2 * VL - 2 * VB)
        return result

    rate, data = wavfile.read(bytes_io_file)
    data = data[:, 1]
    scaler = np.max(np.abs(data))
    data = data.astype(np.float) / scaler
    n_samples = data.shape[0]
    d_lookup = diode_lookup(LOOKUP_SAMPLES)
    diode = Waveshaper(d_lookup)
    tone = np.arange(n_samples)
    tone = np.sin(2 * np.pi * tone * MOD_F / rate)
    tone = tone * 0.5
    tone2 = tone.copy()
    data2 = data.copy()
    tone = -tone + data2
    data = data + tone2
    data = diode.transform(data) + diode.transform(-data)
    tone = diode.transform(tone) + diode.transform(-tone)
    result = data - tone
    result /= np.max(np.abs(result))
    result *= scaler
    wavfile.write(bytes_io_file, rate, result.astype(np.int16))
    bytes_io_file.name = fn + fe
    fn, fe = os.path.splitext(bytes_io_file.name)
    return bytes_io_file, fn, fe


class Waveshaper():
    def __init__(self, curve):
        self.curve = curve
        self.n_bins = self.curve.shape[0]

    def transform(self, samples):
        # normalize to 0 < samples < 2
        max_val = np.max(np.abs(samples))
        if max_val >= 1.0:
            result = samples / np.max(np.abs(samples)) + 1.0
        else:
            result = samples + 1.0
        result = result * (self.n_bins - 1) / 2
        return self.curve[result.astype(np.int)]


@loader.tds
class voicetoolsMod(loader.Module):
    """Change, pitch, enhance your Voice. Also includes optional automatic mode."""
    strings = {
        "name": "VoiceTools",
        "downloading": "<b>[VoiceTools]</b> Message is being downloaded...",
        "vc_start": "<b>[VoiceTools]</b> Auto VoiceChanger activated.",
        "vc_stopped": "<b>[VoiceTools]</b> Auto VoiceChanger deactivated.",
        "vcanon_start": "<b>[VoiceTools]</b> Auto AnonVoice activated.",
        "vcanon_stopped": "<b>[VoiceTools]</b> Auto AnonVoice deactivated.",
        "nr_start": "<b>[VoiceTools]</b> Auto VoiceEnhancer activated.",
        "nr_stopped": "<b>[VoiceTools]</b> Auto VoiceEnhancer deactivated.",
        "norm_start": "<b>[VoiceTools]</b> Auto VoiceNormalizer activated.",
        "norm_stopped": "<b>[VoiceTools]</b> Auto VoiceNormalizer deactivated.",
        "pitch_start": "<b>[VoiceTools]</b> Auto VoicePitch activated.",
        "pitch_stopped": "<b>[VoiceTools]</b> Auto VoicePitch deactivated.",
        "speed_start": "<b>[VoiceTools]</b> Auto VoiceSpeed activated.",
        "speed_stopped": "<b>[VoiceTools]</b> Auto VoiceSpeed deactivated.",
        "vtauto_stopped": "<b>[VoiceTools]</b> Auto Voice Tools deactivated.",
        "error_file": "<b>[VoiceTools] No file in the reply detected.</b>",
        "nr_level": ("<b>[VoiceTools]</b> Noise reduction level set to {}."),
        "pitch_level": ("<b>[VoiceTools]</b> Pitch level set to {}."),
        "no_nr": "<b>[VoiceTools]</b> Your input was an unsupported noise reduction level.",
        "no_pitch": "<b>[VoiceTools]</b> Your input was an unsupported pitch level.",
        "no_speed": "<b>[VoiceTools]</b> Your input was an unsupported speed level.",
        "noargs": "🚫 <b>No file specified</b>",
        "audiohandler_txt": "<b>[VoiceTools]</b> Audio is being transcoded.",
        "audiodenoiser_txt": "<b>[VoiceTools]</b> Background noise is being removed.",
        "audionormalizer_txt": "<b>[VoiceTools]</b> Audiovolume is being normalized.",
        "dalekvoice_txt": "<b>[VoiceTools]</b> Dalek Voice is being applied.",
        "pitch_txt": "<b>[VoiceTools]</b> Pitch is being applied.",
        "speed_txt": "<b>[VoiceTools]</b> Speed is being applied.",
        "uploading": "<b>[VoiceTools]</b> File is uploading.",
        "makewaves_txt": "<b>[VoiceTools]</b> Speech waves are being applied.",
        "_cfg_pitch_lvl": "Set the desired pitch level for auto pitch.",
        "_cfg_nr_lvl": "Set the desired noisereduction level.",
        "_cfg_vg_lvl": "Set the desired volume gain level for auto pitch.",
        "_cfg_speed_lvl": "Set the desired speed level for auto speed.",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "pitch_lvl",
                "0",
                doc=lambda: self.strings("_cfg_pitch_lvl"),
                validator=loader.validators.Float(minimum=-18, maximum=18),
            ),
            loader.ConfigValue(
                "nr_lvl",
                "0.85",
                doc=lambda: self.strings("_cfg_nr_lvl"),
                validator=loader.validators.Float(minimum=0.01, maximum=1),
            ),
            loader.ConfigValue(
                "vg_lvl",
                "3",
                doc=lambda: self.strings("_cfg_vg_lvl"),
                validator=loader.validators.Integer(minimum=-10, maximum=10),
            ),
            loader.ConfigValue(
                "speed_lvl",
                "1",
                doc=lambda: self.strings("_cfg_speed_lvl"),
                validator=loader.validators.Float(minimum=0.25, maximum=3),
            ),
        )
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._id = (await client.get_me(True)).user_id

    async def get_media(self, message: Message, inline_msg, silent):
        reply = await message.get_reply_message()
        m = None
        if reply and reply.media:
            m = reply
        elif message.media:
            m = message
        else:
            return
        if not m:
            file = io.BytesIO(bytes(reply.raw_text, "utf-8"))
        else:
            file = (
                io.BytesIO((await self.fast_download(m.document)).getvalue())
                if silent
                else io.BytesIO(
                    (
                        await self.fast_download(
                            m.document, message_object=inline_msg
                        )
                    ).getvalue()
                )
            )

        file.seek(0)
        return file

    async def vtvccmd(self, message):
        """reply to a file to change the voice"""
        chatid = message.chat_id
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(message, self.strings("error_file", message))
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        vg_lvl = self.config["vg_lvl"]
        nr_lvl = self.config["nr_lvl"]
        file = BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(message=message, text=self.strings("downloading", message), reply_markup={"text": "\u0020\u2800", "data": "empty"})
        file = await self.get_media(replymsg, inline_msg, False)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt", inline_msg))
        file, fn, fe = await audiohandler(file, fn, fe, ".wav", "1", "pcm_s16le")
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiodenoiser_txt", inline_msg))
        file, fn, fe = await audiodenoiser(file, fn, fe, nr_lvl)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audionormalizer_txt", inline_msg))
        file, fn, fe = await audionormalizer(file, fn, fe, vg_lvl)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("dalekvoice_txt", inline_msg))
        file, fn, fe = await dalekvoice(file, fn, fe)
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(inline_msg, self.strings("makewaves_txt", inline_msg))
            file, fn, fe = await audiohandler(file, fn, fe, ".ogg", "2", "libopus")
            file.seek(0)
        file.name = fn + fe
        inline_msg = await utils.answer(inline_msg, self.strings("uploading", inline_msg))
        await message.client.send_file(message.chat_id, file, voice_note=SendAsVoice)
        await message.client.delete_messages(chatid, inline_msg)

    async def vtanoncmd(self, message):
        """reply to a file to change the voice into anonymous"""
        chatid = message.chat_id
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(message, self.strings("error_file", message))
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        vg_lvl = self.config["vg_lvl"]
        file = BytesIO()
        file.name = replymsg.file.name
        nr_lvl = 0.8
        pitch_lvl = -4.5
        inline_msg = await self.inline.form(message=message, text=self.strings("downloading", message), reply_markup={"text": "\u0020\u2800", "data": "empty"})
        file = await self.get_media(replymsg, inline_msg, False)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt", inline_msg))
        file, fn, fe = await audiohandler(file, fn, fe, ".wav", "1", "pcm_s16le")
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiodenoiser_txt", inline_msg))
        file, fn, fe = await audiodenoiser(file, fn, fe, nr_lvl)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audionormalizer_txt", inline_msg))
        file, fn, fe = await audionormalizer(file, fn, fe, vg_lvl)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("dalekvoice_txt", inline_msg))
        file, fn, fe = await dalekvoice(file, fn, fe)
        file.seek(0)
        file, fn, fe = await audiopitcher(file, fn, fe, pitch_lvl)
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(inline_msg, self.strings("makewaves_txt", inline_msg))
            file, fn, fe = await audiohandler(file, fn, fe, ".ogg", "2", "libopus")
            file.seek(0)
        file.name = fn + fe
        inline_msg = await utils.answer(inline_msg, self.strings("uploading", inline_msg))
        await message.client.send_file(message.chat_id, file, voice_note=True)
        await message.client.delete_messages(chatid, inline_msg)

    async def vtpitchcmd(self, message):
        """reply to a file to pitch voice
          - Example: .vtpitch 12
            Possible values between -18 and 18"""
        chatid = message.chat_id
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(message, self.strings("error_file", message))
        pitch_lvl = utils.get_args_raw(message)
        if not represents_pitch(pitch_lvl):
            return await utils.answer(message, self.strings("no_pitch", message))
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        vg_lvl = self.config["vg_lvl"]
        file = BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(message=message, text=self.strings("downloading", message), reply_markup={"text": "\u0020\u2800", "data": "empty"})
        file = await self.get_media(replymsg, inline_msg, False)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt", inline_msg))
        file, fn, fe = await audiohandler(file, fn, fe, ".mp3", "1", "libmp3lame")
        file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".flac", "1", "flac")
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("pitch_txt", inline_msg))
        file, fn, fe = await audiopitcher(file, fn, fe, float(pitch_lvl))
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audionormalizer_txt", inline_msg))
        file, fn, fe = await audionormalizer(file, fn, fe, vg_lvl)
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(inline_msg, self.strings("makewaves_txt", inline_msg))
            file, fn, fe = await audiohandler(file, fn, fe, ".ogg", "2", "libopus")
            file.seek(0)
        file.name = fn + fe
        inline_msg = await utils.answer(inline_msg, self.strings("uploading", inline_msg))
        await message.client.send_file(message.chat_id, file, voice_note=True)
        await message.client.delete_messages(chatid, inline_msg)

    async def vtspeedcmd(self, message):
        """reply to a file to increase speed and reduce length
          - Example: .vtspeed 1.5
            Possible values between 0.25 - 3"""
        chatid = message.chat_id
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(message, self.strings("error_file", message))
        speed_lvl = utils.get_args_raw(message)
        if not represents_speed(speed_lvl):
            return await utils.answer(message, self.strings("no_speed", message))
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        vg_lvl = self.config["vg_lvl"]
        file = BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(message=message, text=self.strings("downloading", message), reply_markup={"text": "\u0020\u2800", "data": "empty"})
        file = await self.get_media(replymsg, inline_msg, False)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt", inline_msg))
        file, fn, fe = await audiohandler(file, fn, fe, ".mp3", "1", "libmp3lame")
        file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".flac", "1", "flac")
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("speed_txt", inline_msg))
        file, fn, fe = await audiospeedup(file, fn, fe, float(speed_lvl))
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audionormalizer_txt", inline_msg))
        file, fn, fe = await audionormalizer(file, fn, fe, vg_lvl)
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(inline_msg, self.strings("makewaves_txt", inline_msg))
            file, fn, fe = await audiohandler(file, fn, fe, ".ogg", "2", "libopus")
            file.seek(0)
        file.name = fn + fe
        inline_msg = await utils.answer(inline_msg, self.strings("uploading", inline_msg))
        await message.client.send_file(message.chat_id, file, voice_note=SendAsVoice)
        await message.client.delete_messages(chatid, inline_msg)

    async def vtenhcmd(self, message):
        """reply to a file to enhance voice quality with
         - Volume normalize
         - Background NoiseReduce (set your noisereduce level before)"""
        chatid = message.chat_id
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(message, self.strings("error_file", message))
        nr_lvl = self.config["nr_lvl"]
        vg_lvl = self.config["vg_lvl"]
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        file = BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(message=message, text=self.strings("downloading", message), reply_markup={"text": "\u0020\u2800", "data": "empty"})
        file = await self.get_media(replymsg, inline_msg, False)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt", inline_msg))
        file, fn, fe = await audiohandler(file, fn, fe, ".mp3", "1", "libmp3lame")
        file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".wav", "1", "pcm_s16le")
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiodenoiser_txt", inline_msg))
        file, fn, fe = await audiodenoiser(file, fn, fe, nr_lvl)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audionormalizer_txt", inline_msg))
        file, fn, fe = await audionormalizer(file, fn, fe, vg_lvl)
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(inline_msg, self.strings("makewaves_txt", inline_msg))
            file, fn, fe = await audiohandler(file, fn, fe, ".ogg", "2", "libopus")
            file.seek(0)
        file.name = fn + fe
        inline_msg = await utils.answer(inline_msg, self.strings("uploading", inline_msg))
        await message.client.send_file(message.chat_id, file, voice_note=SendAsVoice)
        await message.client.delete_messages(chatid, inline_msg)

    async def vtnormcmd(self, message):
        """reply to a file to normalize volume"""
        chatid = message.chat_id
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(message, self.strings("error_file", message))
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        vg_lvl = self.config["vg_lvl"]
        file = BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(message=message, text=self.strings("downloading", message), reply_markup={"text": "\u0020\u2800", "data": "empty"})
        file = await self.get_media(replymsg, inline_msg, False)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt", inline_msg))
        inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt", inline_msg))
        file, fn, fe = await audiohandler(file, fn, fe, ".mp3", "1", "libmp3lame")
        file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".wav", "1", "pcm_s16le")
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audionormalizer_txt", inline_msg))
        file, fn, fe = await audionormalizer(file, fn, fe, vg_lvl)
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(inline_msg, self.strings("makewaves_txt", inline_msg))
            file, fn, fe = await audiohandler(file, fn, fe, ".ogg", "2", "libopus")
            file.seek(0)
        file.name = fn + fe
        inline_msg = await utils.answer(inline_msg, self.strings("uploading", inline_msg))
        await message.client.send_file(message.chat_id, file, voice_note=SendAsVoice)
        await message.client.delete_messages(chatid, inline_msg)

    async def vtmp3cmd(self, message: Message):
        """reply to a file to convert it to mp3"""
        chatid = message.chat_id
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        if not replymsg.media:
            return await utils.answer(message, self.strings("error_file", message))
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        file = BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(message=message, text=self.strings("downloading", message), reply_markup={"text": "\u0020\u2800", "data": "empty"})
        file = await self.get_media(replymsg, inline_msg, False)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("audiohandler_txt", inline_msg))
        file, fn, fe = await audiohandler(file, fn, fe, ".mp3", "1", "libmp3lame")
        file.seek(0)
        file.name = fn + fe
        inline_msg = await utils.answer(inline_msg, self.strings("uploading", inline_msg))
        # await message.client.send_file(message.chat_id, await self.fast_upload(file), voice_note=False)
        await message.client.send_file(message.chat_id, file, voice_note=False)
        await message.client.delete_messages(chatid, inline_msg)

    async def vtspeechcmd(self, message):
        """reply to a file to convert it to speech"""
        chatid = message.chat_id
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        if not replymsg.media:
            return await utils.answer(message, self.strings("error_file", message))
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        file = BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(message=message, text=self.strings("downloading", message), reply_markup={"text": "\u0020\u2800", "data": "empty"})
        file = await self.get_media(replymsg, inline_msg, False)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(inline_msg, self.strings("makewaves_txt", inline_msg))
        file, fn, fe = await audiohandler(file, fn, fe, ".ogg", "2", "libopus")
        file.seek(0)
        file.name = fn + fe
        inline_msg = await utils.answer(inline_msg, self.strings("uploading", inline_msg))
        await message.client.send_file(message.chat_id, file, voice_note=True)
        await message.client.delete_messages(chatid, inline_msg)

    async def vtautovccmd(self, message):
        """Turns on AutoVoiceChanger for your own Voicemessages in the chat"""
        vc_chats = self._db.get(__name__, "vc_watcher", [])
        chatid = message.chat_id
        chatid_str = str(chatid)
        if chatid_str not in vc_chats:
            vc_chats.append(chatid_str)
            self._db.set(__name__, "vc_watcher", vc_chats)
            await utils.answer(message, self.strings("vc_start", message))
        else:
            vc_chats.remove(chatid_str)
            self._db.set(__name__, "vc_watcher", vc_chats)
            await utils.answer(message, self.strings("vc_stopped", message))

    async def vtautoanoncmd(self, message):
        """Turns on AutoAnonVoice for your own Voicemessages in the chat"""
        vcanon_chats = self._db.get(__name__, "vcanon_watcher", [])
        chatid = message.chat_id
        chatid_str = str(chatid)
        if chatid_str not in vcanon_chats:
            vcanon_chats.append(chatid_str)
            self._db.set(__name__, "vcanon_watcher", vcanon_chats)
            await utils.answer(message, self.strings("vcanon_start", message))
        else:
            vcanon_chats.remove(chatid_str)
            self._db.set(__name__, "vcanon_watcher", vcanon_chats)
            await utils.answer(message, self.strings("vcanon_stopped", message))

    async def vtautonrcmd(self, message):
        """Turns on AutoNoiseReduce for your own Voicemessages in the chat"""
        nr_chats = self._db.get(__name__, "nr_watcher", [])
        chatid = message.chat_id
        chatid_str = str(chatid)
        if chatid_str not in nr_chats:
            nr_chats.append(chatid_str)
            self._db.set(__name__, "nr_watcher", nr_chats)
            await utils.answer(message, self.strings("nr_start", message))
        else:
            nr_chats.remove(chatid_str)
            self._db.set(__name__, "nr_watcher", nr_chats)
            await utils.answer(message, self.strings("nr_stopped", message))

    async def vtautonormcmd(self, message):
        """Turns on AutoVoiceNormalizer for your own Voicemessages in the chat"""
        norm_chats = self._db.get(__name__, "norm_watcher", [])
        chatid = message.chat_id
        chatid_str = str(chatid)
        if chatid_str not in norm_chats:
            norm_chats.append(chatid_str)
            self._db.set(__name__, "norm_watcher", norm_chats)
            await utils.answer(message, self.strings("norm_start", message))
        else:
            norm_chats.remove(chatid_str)
            self._db.set(__name__, "norm_watcher", norm_chats)
            await utils.answer(message, self.strings("norm_stopped", message))

    async def vtautospeedcmd(self, message):
        """Turns on AutoSpeed for your own Voicemessages in the chat"""
        speed_chats = self._db.get(__name__, "speed_watcher", [])
        chatid = message.chat_id
        chatid_str = str(chatid)
        if chatid_str not in speed_chats:
            speed_chats.append(chatid_str)
            self._db.set(__name__, "speed_watcher", speed_chats)
            await utils.answer(message, self.strings("speed_start", message))
        else:
            speed_chats.remove(chatid_str)
            self._db.set(__name__, "speed_watcher", speed_chats)
            await utils.answer(message, self.strings("speed_stopped", message))

    async def vtautopitchcmd(self, message):
        """Turns on AutoVoiceNormalizer for your own Voicemessages in the chat"""
        pitch_chats = self._db.get(__name__, "pitch_watcher", [])
        chatid = message.chat_id
        chatid_str = str(chatid)
        if chatid_str not in pitch_chats:
            pitch_chats.append(chatid_str)
            self._db.set(__name__, "pitch_watcher", pitch_chats)
            await utils.answer(message, self.strings("pitch_start", message))
        else:
            pitch_chats.remove(chatid_str)
            self._db.set(__name__, "pitch_watcher", pitch_chats)
            await utils.answer(message, self.strings("pitch_stopped", message))

    async def vtautostopcmd(self, message):
        """Turns off AutoVoice for your own Voicemessages in the chat"""
        norm_chats = self._db.get(__name__, "norm_watcher", [])
        nr_chats = self._db.get(__name__, "nr_watcher", [])
        vc_chats = self._db.get(__name__, "vc_watcher", [])
        pitch_chats = self._db.get(__name__, "pitch_watcher", [])
        vcanon_chats = self._db.get(__name__, "vcanon_watcher", [])
        speed_chats = self._db.get(__name__, "speed_watcher", [])
        chatid = message.chat_id
        chatid_str = str(chatid)
        if chatid_str in norm_chats:
            norm_chats.remove(chatid_str)
            self._db.set(__name__, "norm_watcher", norm_chats)
        if chatid_str in nr_chats:
            nr_chats.remove(chatid_str)
            self._db.set(__name__, "nr_watcher", nr_chats)
        if chatid_str in vc_chats:
            vc_chats.remove(chatid_str)
            self._db.set(__name__, "vc_watcher", vc_chats)
        if chatid_str in pitch_chats:
            pitch_chats.remove(chatid_str)
            self._db.set(__name__, "pitch_watcher", pitch_chats)
        if chatid_str in vcanon_chats:
            vcanon_chats.remove(chatid_str)
            self._db.set(__name__, "vcanon_watcher", vcanon_chats)
        if chatid_str in speed_chats:
            speed_chats.remove(chatid_str)
            self._db.set(__name__, "speed_watcher", speed_chats)
        await utils.answer(message, self.strings("vtauto_stopped", message))

    async def watcher(self, message):
        chatid = message.chat_id
        chatid_str = str(chatid)
        norm_chats = self._db.get(__name__, "norm_watcher", [])
        nr_chats = self._db.get(__name__, "nr_watcher", [])
        vc_chats = self._db.get(__name__, "vc_watcher", [])
        pitch_chats = self._db.get(__name__, "pitch_watcher", [])
        vcanon_chats = self._db.get(__name__, "vcanon_watcher", [])
        speed_chats = self._db.get(__name__, "speed_watcher", [])
        chat = await message.get_chat()
        chattype = await getchattype(message)
        if (chatid_str not in nr_chats
                and chatid_str not in vc_chats
                and chatid_str not in norm_chats
                and chatid_str not in pitch_chats
                and chatid_str not in vcanon_chats
                and chatid_str not in speed_chats):
            return
        if (
            chattype != "channel"
            and message.sender_id != self._id
            or chattype == "channel"
            and not chat.admin_rights.delete_messages
        ):
            return
        if not message.voice or message.via_bot or message.forward:
            return
        if message.reply:
            reply = await message.get_reply_message()
        nr_lvl = self.config["nr_lvl"]
        pitch_lvl = self.config["pitch_lvl"]
        vg_lvl = self.config["vg_lvl"]
        speed_lvl = self.config["speed_lvl"]
        if chatid_str in vc_chats:
            nr_lvl = 0.8
        if chatid_str in vcanon_chats:
            nr_lvl = 0.8
            pitch_lvl = -4.5
        msgs = await message.forward_to(self._id)
        await message.client.delete_messages(chatid, message)
        file = BytesIO()
        file.name = msgs.file.name
        file = await self.get_media(msgs, msgs, True)
        filename = msgs.file.name or "voice"
        ext = msgs.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        file.seek(0)
        await message.client.delete_messages(self._id, msgs)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".mp3", "1", "libmp3lame")
        file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".wav", "1", "pcm_s16le")
        file.seek(0)
        if chatid_str in nr_chats or chatid_str in vcanon_chats or chatid_str in vc_chats:
            file, fn, fe = await audiodenoiser(file, fn, fe, nr_lvl)
            file.seek(0)
        if chatid_str in norm_chats or chatid_str in vcanon_chats or chatid_str in vc_chats:
            file, fn, fe = await audionormalizer(file, fn, fe, vg_lvl)
            file.seek(0)
        if chatid_str in vc_chats or chatid_str in vcanon_chats:
            file, fn, fe = await dalekvoice(file, fn, fe)
            file.seek(0)
        if chatid_str in pitch_chats or chatid_str in vcanon_chats:
            file, fn, fe = await audiopitcher(file, fn, fe, pitch_lvl)
            file.seek(0)
        if chatid_str in speed_chats:
            file, fn, fe = await audiospeedup(file, fn, fe, speed_lvl)
            file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".ogg", "2", "libopus")
        file.seek(0)
        file.name = fn + fe
        if reply:
            await message.client.send_file(message.chat_id, file, voice_note=True, reply_to=reply)
        else:
            await message.client.send_file(message.chat_id, file, voice_note=True)
