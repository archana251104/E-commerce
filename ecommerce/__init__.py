
try:
    from . import admin_fix
    print("✅ Admin fix loaded successfully!")
except Exception as e:
    print(f"⚠️ Admin fix could not be loaded: {e}")