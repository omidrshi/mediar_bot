import json
import os
import requests
from django.http import JsonResponse
from django.views import View
from .models import Chat, Media

TELEGRAM_URL = "https://api.telegram.org/bot"
TUTORIAL_BOT_TOKEN = "1380036001:AAHWFdMS1SZ7b1ATUdC9KF_xqwOjmUwL-ck"
BASE_URL = "https://mediar.pythonanywhere.com"

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

    def post(self, request, *args, **kwargs):

        t_data = json.loads(request.body)
        t_message = t_data["message"]
        t_chat = t_message["chat"]
        chat_obj = Chat.objects.filter(chat_id=t_chat['id']).first()
        if chat_obj:
            chat_obj.first_name = t_chat['first_name']
            chat_obj.last_name = t_chat['last_name']
            chat_obj.is_bot = t_message['from']['is_bot']
            chat_obj.save()
        else:
            chat_obj = Chat(chat_id=t_chat['id'], first_name=t_chat['first_name'], last_name=t_chat['last_name'], is_bot=t_message['from']['is_bot'])
            chat_obj.save()

        if chat_obj.is_admin:
            self.check_file_uploading(t_message)

        try:
            text = t_message["text"].strip().lower()
        except Exception as e:
            return JsonResponse({"ok": "POST request processed"})

        text = text.lstrip("/")

        msg = text

        reply_markup = json.dumps(self.reply_markup)

        self.send_message('123', t_chat["id"], reply_markup)
        # self.send_document('BQACAgQAAxkBAANIXxl9s8xD3tBH6l0ISaTCWbHTqX8AAvsJAAIdnMhQLXdjXvOGAAF2GgQ', t_chat["id"], 'hello', reply_markup)

        return JsonResponse({"ok": "POST request processed"})

    @ staticmethod
    def send_message(message, chat_id, reply_markup):
        data = {
            "chat_id": chat_id,
            "text": message,
            'reply_markup': reply_markup,
            "parse_mode": "Markdown",
        }
        response = requests.post(
            f"{TELEGRAM_URL}{TUTORIAL_BOT_TOKEN}/sendMessage", data=data
        )
        print(response.json())

    @ staticmethod
    def send_document(document, chat_id, caption, reply_markup):
        data = {
            "chat_id": chat_id,
            "caption": caption,
            'document': document,
            "parse_mode": "Markdown",
            'reply_markup': reply_markup,
        }
        response = requests.post(
            f"{TELEGRAM_URL}{TUTORIAL_BOT_TOKEN}/sendDocument", data=data
        )
        print(response.json())

    @ staticmethod
    def check_file_uploading(t_message):
        if "document" in t_message:
            media = Media(file_id=t_message['document']['file_id'], file_name=t_message['document']['file_name'])
            media.save()
            print('Uploading was completed ...')
