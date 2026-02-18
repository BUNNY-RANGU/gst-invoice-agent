from app.agents.auth_agent import AuthAgent
import os

def test():
    auth = AuthAgent()
    print("Attempting to register user 'testuser'...")
    result = auth.register_user(
        username="testuser",
        email="test@example.com",
        password="Password123",
        full_name="Test User"
    )
    print(f"Result: {result}")

if __name__ == "__main__":
    test()
