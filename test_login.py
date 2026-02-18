from app.agents.auth_agent import AuthAgent
import os

def test():
    auth = AuthAgent()
    # Test user from previous test_registration.py
    print("Attempting to login user 'testuser'...")
    result = auth.login_user(
        username="testuser",
        password="Password123"
    )
    print(f"Result: {result}")

if __name__ == "__main__":
    test()
