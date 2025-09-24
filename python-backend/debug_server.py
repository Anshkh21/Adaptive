#!/usr/bin/env python3
"""
Debug script to test Python backend startup
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("config.env")

async def test_imports():
    """Test all imports"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import fastapi
        print("✅ FastAPI imported")
        
        import uvicorn
        print("✅ Uvicorn imported")
        
        import motor
        print("✅ Motor imported")
        
        import beanie
        print("✅ Beanie imported")
        
        # Test app imports
        from app.main import app
        print("✅ App main imported")
        
        from app.database import init_db
        print("✅ Database module imported")
        
        from app.models.user import User
        print("✅ User model imported")
        
        from app.models.assessment import Assessment
        print("✅ Assessment model imported")
        
        from app.models.question import Question
        print("✅ Question model imported")
        
        from app.models.aptitude_test import AptitudeTest
        print("✅ AptitudeTest model imported")
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_database():
    """Test database connection"""
    try:
        print("\nTesting database connection...")
        from app.database import init_db
        await init_db()
        print("✅ Database connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_server():
    """Test server startup"""
    try:
        print("\nTesting server startup...")
        from app.main import app
        
        # Test if app can be created
        print(f"✅ FastAPI app created: {app.title}")
        print(f"✅ App version: {app.version}")
        
        # Test routes
        routes = [route.path for route in app.routes]
        print(f"✅ Routes registered: {len(routes)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🔍 Python Backend Debug Test")
    print("=" * 50)
    
    # Test imports
    imports_ok = await test_imports()
    if not imports_ok:
        print("\n❌ Import tests failed!")
        return False
    
    # Test database
    db_ok = await test_database()
    if not db_ok:
        print("\n❌ Database tests failed!")
        return False
    
    # Test server
    server_ok = await test_server()
    if not server_ok:
        print("\n❌ Server tests failed!")
        return False
    
    print("\n✅ All tests passed! Backend should work.")
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
