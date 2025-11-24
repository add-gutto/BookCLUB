import json
import base64
from django.core.files.base import ContentFile
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from user.models import User
from grupo.models import Topico, Mensagem


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
        imagem_base64 = data.get("imagem")  # Recebe a imagem em Base64
        capitulo = data.get("spoiler_capitulo")
        is_spoiler = True if capitulo else False

        # ========= SALVAR NO BANCO ========= #
        msg = await self.save_message(
            topico_id=self.chat_id,
            user_id=user_id,
            conteudo=message,
            capitulo=capitulo,
            is_spoiler=is_spoiler,
            imagem_base64=imagem_base64
        )

        # ========= ENVIAR AOS USUÁRIOS ========= #
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "id": msg.id,
                "message": msg.conteudo,
                "user_id": user_id,
                "username": username,
                "is_spoiler": msg.is_spoiler,
                "capitulo": msg.capitulo,
                "imagem_url": msg.imagem.url if msg.imagem else None,
                "timestamp": msg.criado_em.strftime("%H:%M"),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    # ========= BANCO DE DADOS ========= #
    @database_sync_to_async
    def save_message(self, topico_id, user_id, conteudo, capitulo, is_spoiler, imagem_base64=None):
        user = User.objects.filter(id=user_id).first()
        topico = Topico.objects.get(id=topico_id)

        msg = Mensagem.objects.create(
            topico=topico,
            usuario=user,
            conteudo=conteudo,
            capitulo=capitulo if capitulo else None,
            is_spoiler=is_spoiler
        )

        if imagem_base64:
            # Decodifica a imagem e salva no ImageField
            format, imgstr = imagem_base64.split(';base64,')
            ext = format.split('/')[-1]  # jpg, png etc.
            file_name = f"msg_{msg.id}.{ext}"
            msg.imagem.save(file_name, ContentFile(base64.b64decode(imgstr)), save=True)

        return msg
