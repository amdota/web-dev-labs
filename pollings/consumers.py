import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import AnonymousUser


class PollingsConsumer(WebsocketConsumer):
    online_users = []

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.common_group_name = "common"
        self.admin_group_name = "admin"

    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)(
            self.common_group_name,
            self.channel_name
        )
        user = self.scope["user"]
        if type(user) is not AnonymousUser:
            self.online_users.append(user.username)
            async_to_sync(self.channel_layer.group_send)(
                self.admin_group_name,
                {
                    "type": "added_new_user",
                    "username": user.username,
                }
            )

        if user.is_staff:
            self.send(json.dumps(
                {
                    "type": "list_of_online_users",
                    "users": self.online_users,
                }
            ))
            async_to_sync(self.channel_layer.group_add)(
                self.admin_group_name,
                self.channel_name
            )

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)

        if data["type"] == "added_new_question":
            async_to_sync(self.channel_layer.group_send)(
                self.common_group_name,
                {
                    "type": "added_new_question",
                    "message": data["message"],
                    'sender_channel_name': self.channel_name
                }
            )
        elif data["type"] == "deleted_question":
            async_to_sync(self.channel_layer.group_send)(
                self.common_group_name,
                {
                    "type": "deleted_question",
                    "message": data["message"],
                    'questionId': data["questionId"],
                    'sender_channel_name': self.channel_name,
                }
            )
        elif data["type"] == "vote_for_answer":
            async_to_sync(self.channel_layer.group_send)(
                self.common_group_name,
                {
                    "type": "vote_for_answer",
                    "message": data["message"],
                    'answerId': data["answerId"],
                    'questionId': data["questionId"],
                    'sender_channel_name': self.channel_name,
                }
            )

    def disconnect(self, code):
        user = self.scope["user"]
        async_to_sync(self.channel_layer.group_discard)(
            self.common_group_name,
            self.channel_name
        )

        if type(user) is not AnonymousUser:
            if user.is_staff:
                async_to_sync(self.channel_layer.group_discard)(
                    self.admin_group_name,
                    self.channel_name
                )

            self.online_users.remove(user.username)

            async_to_sync(self.channel_layer.group_send)(
                self.admin_group_name,
                {
                    "type": "user_disconnected",
                    "username": user.username,
                }
            )

    def added_new_question(self, event):
        if self.channel_name != event['sender_channel_name']:
            self.send(text_data=json.dumps(event))

    def deleted_question(self, event):
        if self.channel_name != event['sender_channel_name']:
            self.send(text_data=json.dumps(event))

    def vote_for_answer(self, event):
        if self.channel_name != event['sender_channel_name']:
            self.send(text_data=json.dumps(event))

    def added_new_user(self, event):
        self.send(text_data=json.dumps(event))

    def user_disconnected(self, event):
        self.send(text_data=json.dumps(event))
