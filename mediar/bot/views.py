import json
import os
import requests
from django.http import JsonResponse
from django.views import View
from .models import Chat, Media, Ad
from django.db.models import Q

TELEGRAM_URL = "https://api.telegram.org/bot"
TUTORIAL_BOT_TOKEN = "1373827281:AAEwxMUTNNMeK34sOAVMfAaq6lnw0wLKF3c"
BASE_URL = "https://b9e026cbfd55.ngrok.io"
CHANNEL_ID = "@mediargroup"

# https://api.telegram.org/bot<token>/setWebhook?url=<url>/webhooks/tutorial/


class SetWebhook(View):
    def get(self, request, *args, **kwargs):
        res = requests.get(url=f"https://api.telegram.org/bot{TUTORIAL_BOT_TOKEN}/setWebhook?url={BASE_URL}/bot/webhook")
        return JsonResponse(res.json())


class Webhook(View):
    reply_markup = {
        'keyboard': [
            [{'text': 'خانه'}],
            [{'text': 'second button'}]
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }

    WELCOME_MESSAGE = "برای جستجو کافیه عنوان کتاب یا نویسنده ی دلخواهتو وارد کنی. یادت باشه با جستجوی فارسی، کتاب های به زبان فارسی نمایش داده میشه. پس برای کتاب های انگلیسی، عنوان یا نویسنده رو انگلیسی جستجو کن."
    WELCOME_MESSAGE_JOINED = "سلام!\nبه مدیار خوش اومدی.اینجا هر کتابی که بخوای رو‌ میتونی جستجو کنی و کاملا رایگان دانلود کنی.تازه این اول ماجراست! به زودی کلی چیز هیجان انگیز دیگه هم براتون داریم.\nپس مارو به دوستاتون معرفی کنید!\n🔰 برای جستجو کافیه عنوان کتاب یا نویسنده رو وارد کنی. اگه فارسی جستجو کنی کتاب فارسی تحویل میگیری پس برای دریافت کتاب انگلیسی اسمشو انگلیسی جستجو کن.\n❌در ضمن حواست باشه که غلط ننویسی!! تا جایی که اسمشو بلدی بنویس بقیه اش با ما😉"

    def post(self, request, *args, **kwargs):

        t_data = json.loads(request.body)

        # Check if got call back query and send the answer
        if 'callback_query' in t_data:
            if 'data' in t_data['callback_query'] and t_data['callback_query']['data'] == 'joined':
                if self.check_channel_member(CHANNEL_ID, t_data['callback_query']['from']['id']):
                    self.send_answer_to_callback(t_data['callback_query']['id'], 'تبریک ... شما عضو مدیار شدید')
                    self.send_message(self.WELCOME_MESSAGE, t_data['callback_query']['message']['chat']['id'], '')
                else:
                    self.send_answer_to_callback(t_data['callback_query']['id'], 'هنوز عضو کانال نشده اید !')
            self.send_answer_to_callback(t_data['callback_query']['id'], '')
            return JsonResponse({"ok": "POST request processed"})

        # if message is not Callback query extract info
        if "message" in t_data:
            t_message = t_data["message"]
            t_chat = t_message["chat"]

            chat_obj = Chat.objects.filter(chat_id=t_chat['id']).first()
            if chat_obj:
                chat_obj.first_name = t_chat['first_name'] if 'first_name' in t_chat else None
                chat_obj.last_name = t_chat['last_name'] if 'last_name' in t_chat else None
                chat_obj.username = t_chat['username'] if 'username' in t_chat else None
                chat_obj.is_bot = t_message['from']['is_bot']
                chat_obj.save()
            else:
                chat_obj = Chat(chat_id=t_chat['id'],
                                first_name=t_chat['first_name'] if 'first_name' in t_chat else None,
                                last_name=t_chat['last_name'] if 'last_name' in t_chat else None,
                                username=t_chat['username'] if 'username' in t_chat else None,
                                is_bot=t_message['from']['is_bot'])
                chat_obj.save()

            if chat_obj.status == "banned":
                self.send_message("شما اجازه دسترسی به ربات را ندارید !\nبرای اطلاعات بیشتر با پشتیبانی در ارتباط باشید", chat_obj.chat_id, '')
                return JsonResponse({"ok": "POST request processed"})

            # if get a message we should check the joining
            if not self.check_channel_member(CHANNEL_ID, t_message['from']['id']):
                self.send_message_to_join_channel(chat_obj.chat_id)
                return JsonResponse({"ok": "POST request processed"})

            # Check if admin uploads a file
            if chat_obj.is_admin and "document" in t_message:
                self.check_file_uploading(t_message)
                return JsonResponse({"ok": "POST request processed"})

            text = t_message["text"]

            if text == "/start":
                self.send_message(self.WELCOME_MESSAGE_JOINED, chat_obj.chat_id, '')
                return JsonResponse({"ok": "POST request processed"})

            if text[0] == "📚":
                media = Media.objects.filter(title=text[2:]).first()
                if media:
                    media.views_count = media.views_count + 1
                    media.save()
                    self.send_document(media.file_id, chat_obj.chat_id, media.title + "\n\n@mediarbot")
                    self.send_ads(chat_obj.chat_id)
                    return JsonResponse({"ok": "POST request processed"})

            results = self.search_in_database(text)
            self.send_message(f'{len(results)} مورد یافت شد ، حالا کتاب مورد نظر خودتو انتخاب کن. اگه چیزی که میخوای توی لیست نبود اصلا نگران نباش! ما در اسرع وقت برات حاضرش میکنیم!', chat_obj.chat_id, results)
            return JsonResponse({"ok": "POST request processed"})
        else:
            return JsonResponse({"ok": "No telegram message was sent"})

    @ staticmethod
    def send_message(message, chat_id, reply_markup):
        reply_markup = {
            'keyboard': reply_markup,
            'resize_keyboard': True,
            'one_time_keyboard': True
        }
        data = {
            "chat_id": chat_id,
            "text": message,
            'reply_markup': json.dumps(reply_markup) if reply_markup['keyboard'] != '' else None,
            "parse_mode": "Markdown",
        }
        response = requests.post(
            f"{TELEGRAM_URL}{TUTORIAL_BOT_TOKEN}/sendMessage", data=data
        )
        # print(response.json())

    @ staticmethod
    def send_document(document, chat_id, caption):
        data = {
            "chat_id": chat_id,
            "caption": caption,
            'document': document,
            "parse_mode": "Markdown",
        }
        response = requests.post(
            f"{TELEGRAM_URL}{TUTORIAL_BOT_TOKEN}/sendDocument", data=data
        )
        # print(response.json())

    @ staticmethod
    def check_file_uploading(t_message):
        if Media.objects.filter(file_id=t_message['document']['file_id']).count() == 0:
            media = Media(file_id=t_message['document']['file_id'], file_name=t_message['document']['file_name'])
            media.save()
            return True
        else:
            return False

    @ staticmethod
    def check_channel_member(chat_id, user_id):
        data = {
            "chat_id": chat_id,
            "user_id": user_id
        }
        response = requests.post(
            f"{TELEGRAM_URL}{TUTORIAL_BOT_TOKEN}/getChatMember", data=data
        )
        print(response.json())
        if response.status_code == 200:
            if response.json()['result']['status'] in ["member", "creator", "administrator"]:
                return True
        return False

    @ staticmethod
    def send_message_to_join_channel(chat_id):
        text = """برای استفاده از امکانات بات لطفا در کانال ما عضو شوید
@mediargroup
همچنین با دنبال کردن ما در اینستاگرام میتوانید از توسعه بات حمایت کنید
[@mediar_group](https://www.instagram.com/mediar_group/)"""
        reply_markup = {
            'inline_keyboard': [
                [{'text': 'برو به کانال', 'url': 'https://t.me/mediargroup'}],
                [{'text': 'عضو شدم', 'callback_data': 'joined'}]
            ],
        }
        reply_markup = json.dumps(reply_markup)
        data = {
            "chat_id": chat_id,
            "text": text,
            'reply_markup': reply_markup,
            "parse_mode": "Markdown",
        }
        response = requests.post(
            f"{TELEGRAM_URL}{TUTORIAL_BOT_TOKEN}/sendMessage", data=data
        )

    @ staticmethod
    def send_answer_to_callback(callback_query_id, text):
        data = {
            "callback_query_id": callback_query_id,
            "text": text,
        }
        response = requests.post(
            f"{TELEGRAM_URL}{TUTORIAL_BOT_TOKEN}/answerCallbackQuery", data=data
        )
        # print(response.json())

    @ staticmethod
    def search_in_database(query):
        queries = query.split()
        results = Media.objects.filter(Q(status="active"))
        for query in queries:
            results = results.filter(Q(title__icontains=query) | Q(author__icontains=query))
        tmp = [res.title for res in results]
        tmp = [[{'text': "📚 " + t}] for t in list(set(tmp))]
        return tmp

    @ staticmethod
    def send_ads(chat_id):
        global BASE_URL
        ads = Ad.objects.filter(status="active").order_by('?')
        if ads:
            ad = ads[0]
            ad.views_count = ad.views_count + 1
            ad.save()
            data = {
                "chat_id": chat_id,
                "caption": ad.caption,
                'photo': BASE_URL + ad.image.url,
                "parse_mode": "Markdown",
            }
            response = requests.post(
                f"{TELEGRAM_URL}{TUTORIAL_BOT_TOKEN}/sendPhoto", data=data
            )
