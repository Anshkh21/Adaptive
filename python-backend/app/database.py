"""
Database configuration and connection setup
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv

from app.models.user import User
from app.models.assessment import Assessment
from app.models.question import Question
from app.models.aptitude_test import AptitudeTest

load_dotenv("config.env")

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def init_db():
    """Initialize database connection"""
    try:
        # MongoDB connection string
        mongo_url = os.getenv("MONGODB_URI", "mongodb://localhost:27017/adaptive_assessment")
        
        # Create motor client
        db.client = AsyncIOMotorClient(mongo_url)
        db.database = db.client.adaptive_assessment
        
        # Initialize beanie with models
        await init_beanie(
            database=db.database,
            document_models=[User, Assessment, Question, AptitudeTest]
        )
        
        print("✅ MongoDB connected successfully")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise e

async def close_db():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("🔌 Database connection closed")

def get_database():
    """Get database instance"""
    return db.database
