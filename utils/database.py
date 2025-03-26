from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.read_concern import ReadConcern
import os
import dotenv

dotenv.load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

# MongoDB setup
mongo_client = AsyncIOMotorClient(mongo_uri)
db = mongo_client.sisyphus_bot
servers_collection = db.get_collection("servers", read_concern=ReadConcern("majority"))

async def get_guild_config(guild_id: str):
    guild_config = await servers_collection.find_one({"_id": guild_id})
    if not guild_config:
        guild_config = {"_id": guild_id}
    return guild_config

async def save_guild_config(guild_id: str, guild_config: dict):
    # Wait for the operation to complete and get the result
    result = await servers_collection.replace_one(
        {"_id": guild_id},
        guild_config,
        upsert=True
    )
    
    if not result.acknowledged:
        print(f"Warning: Database update for guild {guild_id} was not acknowledged")
    
    return result 