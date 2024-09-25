import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TuConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()  # Acepta la conexión

    async def disconnect(self, close_code):
        pass  # Lógica al desconectar

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Maneja el mensaje recibido y envía una respuesta
        await self.send(text_data=json.dumps({
            'message': data['message']
        }))