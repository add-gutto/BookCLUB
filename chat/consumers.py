import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from user.models import User
from grupo.models import Topico, Mensagem  # ajuste o app corretamente


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_group_name = f"chat_{self.chat_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        message = data.get("message")
        user_id = data.get("user_id")
        username = data.get("username")

        # --- SALVA NO BANCO ---
        msg = await self.save_message(
            topico_id=self.chat_id,
            user_id=user_id,
            conteudo=message
        )

        # envia para todos no grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "user_id": user_id,
                "username": username,
                "timestamp": msg.criado_em.strftime("%H:%M"),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, topico_id, user_id, conteudo):
        user = User.objects.get(id=user_id)
        topico = Topico.objects.get(id=topico_id)
        return Mensagem.objects.create(
            topico=topico,
            usuario=user,
            conteudo=conteudo
        )
