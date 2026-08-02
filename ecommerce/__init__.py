# ecommerce/__init__.py
# Import the admin patch for Python 3.14 compatibility
try:
    from . import admin_patch
except Exception as e:
    print(f"Warning: Could not load admin patch: {e}")