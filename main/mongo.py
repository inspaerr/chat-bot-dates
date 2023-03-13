import uuid

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase, AsyncIOMotorCursor
from datetime import datetime
from .settings import MasterSettings


class MongoManager:
    client: AsyncIOMotorClient = None
    users_col = 'tgusers'
    chat_col = 'chats'
    chat_requests_col = 'chat_requests'

    # user structure
    # {
    #   "tgid": "...",
    #   "name": "...",
    #   "age": "...",
    #   "bio": "...",
    #   "status": 0,
    # }

    # statuses
    # 0 - name
    # 1 - age
    # 2 - bio
    # 3 - everything ready

    async def connect(self):
        self.client = AsyncIOMotorClient(MasterSettings.MONGO_HOST, MasterSettings.MONGO_PORT)

    async def disconnect(self):
        self.client.close()

    async def get_random_chat_request(self, tgid):
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