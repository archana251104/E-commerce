# fix_context.py
import django.template.context

def fixed_copy(self):
    """Fixed __copy__ method for Python 3.14 compatibility"""
    new_context = self.__class__()
    new_context.dicts = self.dicts[:]
    return new_context

# Apply the fix globally
django.template.context.Context.__copy__ = fixed_copy
print("✅ Context patch applied!")