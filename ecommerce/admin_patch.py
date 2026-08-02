# admin_patch.py - Fix for Python 3.14 compatibility
import django.template.context

def fixed_copy(self):
    """Fixed __copy__ method for Context to work with Python 3.14"""
    duplicate = super().__new__(self.__class__)
    duplicate.dicts = self.dicts[:]
    return duplicate

# Apply the patch if the original __copy__ exists
if hasattr(django.template.context.Context, '__copy__'):
    django.template.context.Context.__copy__ = fixed_copy
    print("✅ Admin compatibility patch applied successfully!")
else:
    print("⚠️ No patch needed")