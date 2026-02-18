"""
Authentication Agent
Handle user registration, login and JWT tokens
Author: Bunny Rangu
Day: 11/30
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import sys
import os
import hashlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.models.database import User, SessionLocal

# Security configuration
SECRET_KEY = "gst-invoice-agent-secret-key-bunny-rangu-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthAgent:
    """Handle all authentication operations"""
    
    @staticmethod
    def _hash_password_sha256(password: str) -> str:
        """Pre-hash password using SHA-256 to support any length
        
        This converts passwords of any length to a fixed 64-character string,
        which is safe for bcrypt (72-byte limit).
        
        Args:
            password: Plain text password
            
        Returns:
            SHA-256 hashed password (64 character hex string)
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA-256 + direct bcrypt
        
        Supports passwords of any length by first hashing with SHA-256,
        then applying bcrypt for secure storage.
        """
        import bcrypt
        # First, hash with SHA-256 (generates 64-char string)
        sha256_hash = self._hash_password_sha256(password)
        # Then apply bcrypt on the SHA-256 hash
        # We need to encode the string to bytes for bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(sha256_hash.encode('utf-8'), salt)
        # Return as string for database storage
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash using direct bcrypt
        
        Supports passwords of any length by using the same SHA-256 + bcrypt approach.
        """
        import bcrypt
        try:
            # First, hash with SHA-256 to match the stored hash format
            sha256_hash = self._hash_password_sha256(plain_password)
            # Then verify against the bcrypt hash
            return bcrypt.checkpw(
                sha256_hash.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token
        
        Args:
            data: Data to encode in token
            expires_delta: Token expiry time
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Token data or None if invalid
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            
            if username is None:
                return None
            
            return {"username": username, "role": payload.get("role", "user")}
            
        except JWTError:
            return None
    
    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str = "",
        role: str = "user"
    ) -> Dict:
        """
        Register a new user
        
        Args:
            username: Unique username
            email: User email
            password: Plain text password
            full_name: User's full name
            role: User role (admin/user)
            
        Returns:
            Success/failure dictionary
        """
        db = SessionLocal()
        
        try:
            # Check if username exists
            existing_user = db.query(User).filter(
                User.username == username
            ).first()
            
            if existing_user:
                return {
                    'success': False,
                    'error': f"Username '{username}' already exists"
                }
            
            # Check if email exists
            existing_email = db.query(User).filter(
                User.email == email
            ).first()
            
            if existing_email:
                return {
                    'success': False,
                    'error': f"Email '{email}' already registered"
                }
            
            # Hash password
            hashed_password = self.hash_password(password)
            
            # Create user
            user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                full_name=full_name,
                role=role
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            return {
                'success': True,
                'message': f"User '{username}' registered successfully!",
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            db.close()
    
    def login_user(self, username: str, password: str) -> Dict:
        """
        Login a user and return JWT token
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            Success/failure with token
        """
        db = SessionLocal()
        
        try:
            # Find user
            user = db.query(User).filter(
                User.username == username
            ).first()
            
            if not user:
                return {
                    'success': False,
                    'error': 'Invalid username or password'
                }
            
            # Verify password
            if not self.verify_password(password, user.hashed_password):
                return {
                    'success': False,
                    'error': 'Invalid username or password'
                }
            
            # Check if active
            if user.is_active != "true":
                return {
                    'success': False,
                    'error': 'Account is deactivated'
                }
            
            # Create token
            access_token = self.create_access_token(
                data={
                    "sub": user.username,
                    "role": user.role,
                    "email": user.email
                }
            )
            
            return {
                'success': True,
                'message': f'Welcome back, {user.full_name or user.username}!',
                'access_token': access_token,
                'token_type': 'bearer',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            db.close()
    
    def get_current_user(self, token: str) -> Optional[Dict]:
        """
        Get current user from token
        
        Args:
            token: JWT token
            
        Returns:
            User data or None
        """
        token_data = self.verify_token(token)
        
        if not token_data:
            return None
        
        db = SessionLocal()
        
        try:
            user = db.query(User).filter(
                User.username == token_data['username']
            ).first()
            
            if not user:
                return None
            
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role
            }
            
        finally:
            db.close()


def test_auth_agent():
    """Test authentication agent"""
    print("🧪 TESTING AUTH AGENT\n")
    
    auth = AuthAgent()
    
    # Test 1: Register admin user
    print("Test 1: Register admin user")
    result = auth.register_user(
        username="admin",
        email="admin@aitaxsolutions.com",
        password="Admin@123",
        full_name="System Admin",
        role="admin"
    )
    print(f"✅ {result['message'] if result['success'] else result['error']}\n")
    
    # Test 2: Register regular user
    print("Test 2: Register regular user")
    result = auth.register_user(
        username="bunny",
        email="bunny@example.com",
        password="Bunny@123",
        full_name="Bunny Rangu",
        role="user"
    )
    print(f"✅ {result['message'] if result['success'] else result['error']}\n")
    
    # Test 3: Login with correct credentials
    print("Test 3: Login with correct credentials")
    result = auth.login_user("admin", "Admin@123")
    if result['success']:
        print(f"✅ {result['message']}")
        print(f"   Token: {result['access_token'][:50]}...")
        token = result['access_token']
    else:
        print(f"❌ {result['error']}")
        token = None
    print()
    
    # Test 4: Login with wrong password
    print("Test 4: Login with wrong password")
    result = auth.login_user("admin", "wrongpassword")
    print(f"✅ Correctly rejected: {result['error']}\n")
    
    # Test 5: Verify token
    if token:
        print("Test 5: Verify token")
        user_data = auth.get_current_user(token)
        if user_data:
            print(f"✅ Token valid! User: {user_data['username']} ({user_data['role']})\n")
    
    # Test 6: Duplicate username
    print("Test 6: Duplicate username")
    result = auth.register_user(
        username="admin",
        email="other@example.com",
        password="Test@123",
        full_name="Test User"
    )
    print(f"✅ Correctly rejected: {result['error']}\n")
    
    print("="*50)
    print("✅ ALL AUTH TESTS COMPLETE!")
    print("="*50)


if __name__ == "__main__":
    test_auth_agent()