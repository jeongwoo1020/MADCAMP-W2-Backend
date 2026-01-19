import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chat, Community, User, Member

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.com_uuid = self.scope['url_route']['kwargs']['com_uuid']
        self.room_group_name = f'chat_{self.com_uuid}'

        # 1. 방 그룹에 가입
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # 2. 방 그룹에서 탈퇴
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 3. 클라이언트로부터 메시지 수신
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        # user_id = data.get('user_id') 
        
        user = self.scope['user']
        
        if user.is_anonymous:
            await self.send(text_data=json.dumps({"error": "인증되지 않은 유저입니다."}))
            return

        # DB에 메시지 저장 및 닉네임 가져오기
        sender_info = await self.save_message(user.user_id, self.com_uuid, message)

        # 4. 그룹 전체에 메시지 전송 (브로드캐스팅)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'nickname': sender_info['nickname'],
                'user_id': str(user.user_id)
            }
        )

    # 5. 그룹 메시지 수신 시 처리
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'nickname': event['nickname'],
            'user_id': event['user_id']
        }))

    # DB 작업은 비동기 처리가 필요함
    @database_sync_to_async
    def save_message(self, user_id, com_uuid, content):
        user = User.objects.get(user_id=user_id)
        community = Community.objects.get(com_uuid=com_uuid)
        
        # 채팅 저장
        Chat.objects.create(user_id=user, com_uuid=community, content=content)
        
        # 보낸 사람의 닉네임 가져오기 (우리가 만든 Member 모델 활용)
        member = Member.objects.filter(user_id=user, com_uuid=community).first()
        nickname = member.nick_name if member else user.user_name
        
        return {'nickname': nickname}