"""взаимодействие с базой данных"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase, AsyncIOMotorCursor
from datetime import datetime
from .settings import MasterSettings


class MongoManager:
    """класс для работы с БД
     user structure
     {
       "tgid": "...",
       "name": "...",
       "age": "...",
       "bio": "...",
       "status": 0,
     }

    statuses
    0 - name
    1 - age
    2 - bio
    3 - everything ready
    """
    client: AsyncIOMotorClient = None
    users_col = 'tgusers'
    chat_col = 'chats'
    chat_requests_col = 'chat_requests'

    async def connect(self):
        """открытие соединения с БД"""
        self.client = AsyncIOMotorClient(MasterSettings.MONGO_HOST, MasterSettings.MONGO_PORT)

    async def disconnect(self):
        """закрытие соединения с БД"""
        self.client.close()

    async def get_random_chat_request(self, tgid):
        """подбор собеседника"""
        db: AsyncIOMotorDatabase = self.client[MasterSettings.MONGO_DB]
        collection: AsyncIOMotorCollection = db[self.chat_requests_col]
        request = await collection.aggregate([
            {
                "$match": {
                    "tgid": {"$not": {"$eq": tgid}}
                }
            },
            {
                "$sample": {"size": 1}
            }
        ]).to_list(length=None)
        if len(request) == 0:
            return None
        else:
            return request[0]
    async def user_as_info(self, tgid):
        """получение информации о собеседнике"""
        user = await self.get_user(tgid)
        return f"Информация о твоём(-ей) собеседнике(-це)\n" \
               f"Имя: {user['name']}\n" \
               f"Возраст: {user['age']}\n" \
               f"О себе: {user['bio']}\n"

    async def get_chat(self, tgid):
        """получить чат"""
        db: AsyncIOMotorDatabase = self.client[MasterSettings.MONGO_DB]
        collection: AsyncIOMotorCollection = db[self.chat_col]
        return await collection.find_one({'tgid': tgid})

    async def user_registered(self, tgid):
        """проверка регистрации пользователя"""
        db: AsyncIOMotorDatabase = self.client[MasterSettings.MONGO_DB]
        collection: AsyncIOMotorCollection = db[self.users_col]
        return await collection.find_one({"tgid": tgid})

    async def register_user(self, tgid):
        """регистрация пользоваетля"""
        db: AsyncIOMotorDatabase = self.client[MasterSettings.MONGO_DB]
        collection: AsyncIOMotorCollection = db[self.users_col]
        if not await self.user_registered(tgid):
            await collection.insert_one(
                {
                    "tgid": tgid,
                    "name": None,
                    "age": None,
                    "bio": None,
                    "status": 0
                }
            )

    async def get_user(self, tgid):
        """получение информации о пользователе или его регистрация"""
        db: AsyncIOMotorDatabase = self.client[MasterSettings.MONGO_DB]
        collection: AsyncIOMotorCollection = db[self.users_col]
        user = await collection.find_one({"tgid": tgid})
        if not user:
            await self.register_user(tgid)
        return user

    async def update_user(self, tgid, value):
        """обновить информацию о пользователе"""
        db: AsyncIOMotorDatabase = self.client[MasterSettings.MONGO_DB]
        collection: AsyncIOMotorCollection = db[self.users_col]
        user = await self.get_user(tgid)
        status = user.get('status')
        if status == 0:
            await collection.update_one({"tgid": tgid}, {"$set": {"name": value, "status": 1}})
        elif status == 1:
            await collection.update_one({"tgid": tgid}, {"$set": {"age": value, "status": 2}})
        elif status == 2:
            await collection.update_one({"tgid": tgid}, {"$set": {"bio": value, "status": 3}})

    async def chat_exists(self, tgid):
        """проверка существования чата"""
        db: AsyncIOMotorDatabase = self.client[MasterSettings.MONGO_DB]
        collection: AsyncIOMotorCollection = db[self.chat_col]
        return bool(await collection.find_one({"tgid": tgid}))

    async def start_chat(self, tgid1, tgid2):
        """инициация чата"""
        db: AsyncIOMotorDatabase = self.client[MasterSettings.MONGO_DB]
        collection: AsyncIOMotorCollection = db[self.chat_col]
        if not await self.chat_exists(tgid1):
            await collection.insert_one({"tgid": tgid1, "elsetgid": tgid2})
            return True
        else:
            return False

    async def create_chat_request(self, tgid):
        """создание запроса на начало чата"""
        db: AsyncIOMotorDatabase = self.client[MasterSettings.MONGO_DB]
        collection: AsyncIOMotorCollection = db[self.chat_requests_col]
        if bool(await collection.find_one({"tgid": tgid})):
            return False
        else:
            await collection.insert_one({"tgid": tgid})
            return True

    async def delete_chat_request(self, tgid):
        """удаление запроса на начало чата"""
        db: AsyncIOMotorDatabase = self.client[MasterSettings.MONGO_DB]
        collection: AsyncIOMotorCollection = db[self.chat_requests_col]
        await collection.delete_many({"tgid": tgid})

    async def delete_chat(self, tgid):
        """удалить чат"""
        db: AsyncIOMotorDatabase = self.client[MasterSettings.MONGO_DB]
        collection: AsyncIOMotorCollection = db[self.chat_col]
        await collection.delete_many({"tgid": tgid})