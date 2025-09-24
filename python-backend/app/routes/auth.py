"""
Authentication routes for Python backend
Equivalent to Node.js auth routes
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from app.models.user import User, UserRole
from app.database import get_database

load_dotenv("config.env")

router = APIRouter()
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Increased to 1 hour

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    firstName: str = Field(alias="firstName")
    lastName: str = Field(alias="lastName")
    institution: str
    department: Optional[str] = None
    year: Optional[str] = None
    rollNumber: Optional[str] = Field(None, alias="rollNumber")
    role: UserRole = UserRole.STUDENT
    
    class Config:
        populate_by_name = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class TokenData(BaseModel):
    user_id: Optional[str] = None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check if token is valid
    if not credentials.credentials or credentials.credentials == "undefined" or credentials.credentials == "null":
        print("Invalid token: token is undefined or null")  # Debug log
        raise credentials_exception
    
    try:
        print(f"Validating token: {credentials.credentials[:20]}...")  # Debug log
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            print("No user_id in token payload")  # Debug log
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except jwt.PyJWTError as e:
        print(f"JWT decode error: {e}")  # Debug log
        raise credentials_exception
    
    user = await User.get(token_data.user_id)
    if user is None:
        print(f"User not found for ID: {token_data.user_id}")  # Debug log
        raise credentials_exception
    return user

@router.post("/register", response_model=Token)
async def register(user_data: UserRegister):
    """Register a new user"""
    try:
        print(f"Register request received for email: {user_data.email}")  # Debug log
        
        # Check if user already exists
        existing_user = await User.find_one(User.email == user_data.email)
        if existing_user:
            print(f"Email already exists: {user_data.email}")  # Debug log
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if roll number already exists (if provided)
        if user_data.rollNumber:
            existing_roll = await User.find_one(User.roll_number == user_data.rollNumber)
            if existing_roll:
                print(f"Roll number already exists: {user_data.rollNumber}")  # Debug log
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Roll number already registered"
                )
        
        # Hash password first
        import bcrypt
        salt = bcrypt.gensalt(rounds=12)
        hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), salt).decode('utf-8')
        
        # Create new user with all required fields
        user = User(
            email=user_data.email,
            password=hashed_password,
            first_name=user_data.firstName,
            last_name=user_data.lastName,
            institution=user_data.institution,
            department=user_data.department,
            year=user_data.year,
            roll_number=user_data.rollNumber,
            role=user_data.role
        )
        
        # Save user
        await user.insert()
        print(f"User created successfully: {user.email}")  # Debug log
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token": access_token,  # Add token field for frontend compatibility
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "firstName": user.first_name,  # Use camelCase for frontend
                "lastName": user.last_name,    # Use camelCase for frontend
                "role": user.role,
                "institution": user.institution,
                "department": user.department,
                "year": user.year,
                "rollNumber": user.roll_number  # Use camelCase for frontend
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in register: {e}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login user"""
    try:
        print(f"Login request received for email: {user_data.email}")  # Debug log
        
        # Find user by email
        user = await User.find_one(User.email == user_data.email)
        if not user:
            print(f"User not found for email: {user_data.email}")  # Debug log
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check password
        if not await user.check_password(user_data.password):
            print(f"Invalid password for email: {user_data.email}")  # Debug log
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Update last login
        user.last_login = datetime.now()
        await user.save()
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        print(f"Login successful for email: {user_data.email}")  # Debug log
        
        return {
            "access_token": access_token,
            "token": access_token,  # Add token field for frontend compatibility
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "firstName": user.first_name,  # Use camelCase for frontend
                "lastName": user.last_name,    # Use camelCase for frontend
                "role": user.role,
                "institution": user.institution,
                "department": user.department,
                "year": user.year,
                "rollNumber": user.roll_number  # Use camelCase for frontend
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in login: {e}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "firstName": current_user.first_name,  # Use camelCase for frontend
        "lastName": current_user.last_name,    # Use camelCase for frontend
        "role": current_user.role,
        "institution": current_user.institution,
        "department": current_user.department,
        "year": current_user.year,
        "rollNumber": current_user.roll_number,  # Use camelCase for frontend
        "is_active": current_user.is_active,
        "last_login": current_user.last_login
    }

@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile (alias for /me endpoint)"""
    return {
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "firstName": current_user.first_name,  # Use camelCase for frontend
            "lastName": current_user.last_name,    # Use camelCase for frontend
            "role": current_user.role,
            "institution": current_user.institution,
            "department": current_user.department,
            "year": current_user.year,
            "rollNumber": current_user.roll_number,  # Use camelCase for frontend
            "is_active": current_user.is_active,
            "last_login": current_user.last_login
        }
    }

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client should discard token)"""
    return {"message": "Successfully logged out"}
