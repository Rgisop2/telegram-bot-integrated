import motor.motor_asyncio
from config import DB_NAME, DB_URI

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.link_col = self.db.link_settings
        # <CHANGE> Added admin_col for storing single admin session
        self.admin_col = self.db.admin_session

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            session = None,
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def set_session(self, id, session):
        await self.col.update_one({'id': int(id)}, {'$set': {'session': session}})

    async def get_session(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user['session']
    
    # <CHANGE> Added admin-only session methods
    async def set_admin_session(self, session):
        """Store the single admin session string"""
        await self.admin_col.update_one(
            {'_id': 'admin'},
            {'$set': {'session': session}},
            upsert=True
        )
    
    async def get_admin_session(self):
        """Retrieve the single admin session string"""
        admin = await self.admin_col.find_one({'_id': 'admin'})
        return admin['session'] if admin else None

    async def add_urban_link(self, link):
        """Store a new Urban Links bot link with unique ID"""
        import uuid
        link_id = str(uuid.uuid4())[:8]
        await self.link_col.insert_one({
            '_id': link_id,
            'link': link,
            'created_at': __import__('datetime').datetime.now()
        })
        return link_id

    async def get_all_urban_links(self):
        """Get all stored Urban Links bot links"""
        links = []
        async for doc in self.link_col.find({}):
            links.append({'id': doc['_id'], 'link': doc['link']})
        return links

    async def get_urban_link_by_id(self, link_id):
        """Get specific Urban Links bot link by ID"""
        doc = await self.link_col.find_one({'_id': link_id})
        return doc['link'] if doc else None

db = Database(DB_URI, DB_NAME)
