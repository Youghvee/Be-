# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
# The entire source code is OSSRPL except 'whois' which is MPL
# License: MPL and OSSRPL
""" Userbot module for getting info about any user on Telegram(including you!). """

import os

from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName
from telethon.utils import get_input_location

from AyiinXd import CMD_HELP
from AyiinXd.ayiin import ayiin_cmd

from . import cmd, var


@ayiin_cmd(pattern="info(?: |$)(.*)")
async def who(event):

    await event.edit("`Bentar Ya Jing Gua Cek Dulu...`")

    if not os.path.isdir(var.TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(var.TEMP_DOWNLOAD_DIRECTORY)

    replied_user = await get_user(event)

    try:
        photo, caption = await fetch_info(replied_user, event)
    except AttributeError:
        return event.edit(
            "`Duh Tot Nih Bocah Siapa Ya Kok Gua Ga Tau Dia Siapa...`"
        )

    message_id_to_reply = event.message.reply_to_msg_id

    if not message_id_to_reply:
        message_id_to_reply = None

    try:
        await event.client.send_file(
            event.chat_id,
            photo,
            caption=caption,
            link_preview=False,
            force_document=False,
            reply_to=message_id_to_reply,
            parse_mode="html"
        )

        if not photo.startswith("http"):
            os.remove(photo)
        await event.delete()

    except TypeError:
        await event.edit(caption, parse_mode="html")


async def get_user(event):
    """ Get the user from argument or replied message. """
    if event.reply_to_msg_id and not event.pattern_match.group(1):
        previous_message = await event.get_reply_message()
        replied_user = await event.client(
            GetFullUserRequest(previous_message.from_id))
    else:
        user = event.pattern_match.group(1)

        if user.isnumeric():
            user = int(user)

        if not user:
            self_user = await event.client.get_me()
            user = self_user.id

        if event.message.entities is not None:
            probable_user_mention_entity = event.message.entities[0]

            if isinstance(
                probable_user_mention_entity,
                MessageEntityMentionName
            ):
                user_id = probable_user_mention_entity.user_id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user
        try:
            user_object = await event.client.get_entity(user)
            replied_user = await event.client(
                GetFullUserRequest(user_object.id))
        except (TypeError, ValueError) as err:
            return await event.edit(str(err))

    return replied_user


async def fetch_info(replied_user, event):
    """ Get details from the User object. """
    replied_user_profile_photos = await event.client(
        GetUserPhotosRequest(
            user_id=replied_user.user.id,
            offset=42,
            max_id=0,
            limit=80
        )
    )
    replied_user_profile_photos_count = "Orang tersebut membutuhkan bantuan untuk mengupload gambar profil."
    try:
        replied_user_profile_photos_count = replied_user_profile_photos.count
    except AttributeError:
        pass
    user_id = replied_user.user.id
    first_name = replied_user.user.first_name
    last_name = replied_user.user.last_name
    try:
        dc_id, location = get_input_location(replied_user.profile_photo)
    except Exception as e:
        dc_id = "-"
        str(e)
    common_chat = replied_user.common_chats_count
    username = replied_user.user.username
    user_bio = replied_user.about
    is_bot = replied_user.user.bot
    restricted = replied_user.user.restricted
    verified = replied_user.user.verified
    photo = await event.client.download_profile_photo(
        user_id,
        var.TEMP_DOWNLOAD_DIRECTORY + str(user_id) + ".jpg",
        download_big=True
    )
    first_name = first_name.replace("\u2060", "") if first_name else "-"
    last_name = last_name.replace("\u2060", "") if last_name else "-"
    username = "@{}".format(username) if username else "-"
    user_bio = "-" if not user_bio else user_bio

    caption = "<b>▢ ɪɴғᴏ ᴘᴇɴɢɢᴜɴᴀ</b>\n\n"
    caption += f"⊳ ɴᴀᴍᴀ ᴅᴇᴘᴀɴ: {first_name}\n"
    caption += f"⊳ ᴜsᴇʀɴᴀᴍᴇ : {username}\n"
    caption += f"⊳ ɪᴅ ʟᴜ ʙᴇʀᴀᴘᴀ sɪ ᴊɪɴɢ : <code>{user_id}</code>\n\n"
    caption += f"<a href=\"tg://user?id={user_id}\">{first_name}</a>"

    return photo, caption


CMD_HELP.update(
    {
        "info": f"**Plugin : **`info`\
        \n\n  »  **Perintah :** `{cmd}info <username>` Atau Balas Ke Pesan Pengguna Ketik `{cmd}info`\
        \n  »  **Kegunaan:** Mendapatkan Informasi Pengguna."
    }
)
