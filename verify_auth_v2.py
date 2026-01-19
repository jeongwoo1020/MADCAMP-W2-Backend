import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from api.services import AuthService
from api.models import User

def run_verification():
    print("--- Starting Verification (Login ID Version) ---")
    
    # 1. Register with login_id/password
    print("\n[Test 1] Registering user with Login ID/PW...")
    login_id = "test_login_id_001"
    password = "secretpassword"
    user_name = "AuthTester"
    
    # Clean up if exists
    if User.objects.filter(login_id=login_id).exists():
        User.objects.filter(login_id=login_id).delete()
        print("   (Cleaned up existing test user)")

    try:
        user = AuthService.register_user(
            user_name=user_name, 
            profile_img_url="http://test.com/img.png",
            login_id=login_id,
            password=password
        )
        print(f"   User created: {user.login_id} (UUID: {user.user_id})")
    except Exception as e:
        print(f"   ❌ Registration Failed: {e}")
        return

    # 2. Login with correct credentials
    print("\n[Test 2] Logging in with correct credentials...")
    login_user = AuthService.login_user(login_id, password)
    
    if login_user and login_user.user_id == user.user_id:
        print("   ✅ Login SUCCESS")
    else:
        print("   ❌ Login FAILED")

    # 3. Login with wrong password
    print("\n[Test 3] Logging in with WRONG password...")
    fail_user = AuthService.login_user(login_id, "wrongpassword")
    
    if fail_user is None:
        print("   ✅ Wrong password check SUCCESS")
    else:
        print("   ❌ Wrong password check FAILED")

    # 4. Cleanup
    print("\n[Cleanup] Deleting test user...")
    user.delete()
    print("   Done.")

if __name__ == "__main__":
    run_verification()
