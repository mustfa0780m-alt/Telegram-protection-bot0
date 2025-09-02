from telethon import TelegramClient, events, errors, functions, types

# إعدادات
api_id = 19544986
api_hash = '83d3621e6be385938ba3618fa0f0b543'
bot_token = '8426678140:AAG3721Hak7V0u_ACZOl2pQHzMgY7Udxk4k'
channel_username = '@sutazz'

client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

# حفظ حالة الأعضاء الذين تم تحذيرهم لتجنب إرسال الرسائل أكثر من مرة
warned_users = {}

async def is_subscribed(user_id):
    try:
        member = await client.get_participant(channel_username, user_id)
        return True
    except:
        return False

@client.on(events.NewMessage)
async def handler(event):
    sender = await event.get_sender()
    chat = await event.get_chat()

    if not event.is_group:
        return  # نتعامل فقط مع المجموعات

    user_id = sender.id
    username = f"@{sender.username}" if sender.username else sender.first_name

    subscribed = await is_subscribed(user_id)

    if subscribed:
        # إذا كان مشترك، نرفع أي قيود سابقة
        if user_id in warned_users:
            try:
                await client(functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=chat.id,
                    banned_rights=types.ChatBannedRights(
                        until_date=None,
                        send_messages=False,  # False تعني رفع التقييد
                        send_media=False,
                        send_stickers=False,
                        send_gifs=False,
                        send_games=False,
                        send_inline=False,
                        embed_links=False
                    )
                ))
            except:
                pass
            warned_users.pop(user_id)
        return

    # غير مشترك
    # حذف الرسالة
    try:
        await event.delete()
    except:
        pass

    # إرسال رسالة تنبيهية مرة واحدة فقط
    if user_id not in warned_users:
        await client.send_message(
            chat.id,
            f"عزيزي {username} اشترك في القناة ثم ارجع إلينا نحن ننتظرك \"@sutazz\""
        )
        warned_users[user_id] = True

        # تقييد العضو من إرسال الرسائل
        try:
            await client(functions.messages.EditChatDefaultBannedRightsRequest(
                peer=chat.id,
                banned_rights=types.ChatBannedRights(
                    until_date=None,
                    send_messages=True,  # True تعني منع إرسال الرسائل
                    send_media=True,
                    send_stickers=True,
                    send_gifs=True,
                    send_games=True,
                    send_inline=True,
                    embed_links=True
                )
            ))
        except:
            pass

print("Bot is running...")
client.run_until_disconnected()