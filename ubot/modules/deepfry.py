# Copyright (C) 2019 Nick Filmer (nick80835@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Original source for the deepfrying code (used under the following license): https://github.com/Ovyerus/deeppyer

# MIT License
#
# Copyright (c) 2017 Ovyerus
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import io
from random import randint, uniform

from PIL import Image, ImageEnhance, ImageOps
from telethon.tl.types import DocumentAttributeFilename

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader


@ldr.add(pattern="deepfry")
async def deepfryer(event):
    try:
        frycount = int(event.pattern_match.group(1))
        if frycount < 1:
            raise ValueError
    except ValueError:
        frycount = 1

    replied_fry = True

    if event.is_reply:
        reply_message = await event.get_reply_message()
        data = await check_media(reply_message)

        if isinstance(data, bool):
            await event.edit("`I can't deep fry that!`")
            return
    else:
        data = await check_media(event)
        replied_fry = False

        if isinstance(data, bool):
            await event.edit("`Reply to an image or sticker or caption an image to deep fry it!`")
            return

    # Download photo (highres) as byte array
    await event.edit("`Downloading media…`")
    image = io.BytesIO()
    await event.client.download_media(data, image)
    image = Image.open(image)

    # Fry the image
    await event.edit("`Deep frying media…`")
    image = image.convert("RGB")

    for _ in range(frycount):
        image = await deepfry(image)

    fried_io = io.BytesIO()
    fried_io.name = "image.jpeg"
    image.save(fried_io, "JPEG")
    fried_io.seek(0)

    if replied_fry:
        await event.edit("`Deep frying complete.`")
        await event.reply(file=fried_io)
    else:
        await event.edit("`Deep frying complete.`", file=fried_io)


async def deepfry(img):
    # Crush image to hell and back
    img = ImageOps.posterize(img, randint(3, 7))

    # Generate colour overlay
    overlay = img.copy()
    overlay = ImageEnhance.Contrast(overlay).enhance(uniform(0.7, 1.8))
    overlay = ImageEnhance.Brightness(overlay).enhance(uniform(0.8, 1.3))
    overlay = ImageEnhance.Color(overlay).enhance(uniform(0.7, 1.4))

    # Blend random colors onto and sharpen the image
    img = Image.blend(img, overlay, uniform(0.1, 0.4))
    img = ImageEnhance.Sharpness(img).enhance(randint(5, 200))

    return img


async def check_media(reply_message):
    if reply_message and reply_message.media:
        if reply_message.photo:
            data = reply_message.photo
        elif reply_message.document:
            if DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in reply_message.media.document.attributes:
                return False
            if reply_message.gif or reply_message.video or reply_message.audio or reply_message.voice:
                return False
            data = reply_message.media.document
        else:
            return False
    else:
        return False

    if not data or data is None:
        return False
    else:
        return data
