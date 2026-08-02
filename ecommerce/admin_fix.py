# ecommerce/admin_fix.py
import django.template.context
import copy

def patched_copy(self):
    """Fixed __copy__ method for Python 3.14 - copies ALL attributes"""
    try:
        # Handle RequestContext specially
        if hasattr(self, 'request'):
            duplicate = self.__class__(self.request)
        else:
            duplicate = self.__class__()
        
        # Copy ALL attributes from self to duplicate
        for attr_name in dir(self):
            # Skip private/internal attributes that shouldn't be copied
            if attr_name.startswith('__'):
                continue
            
            try:
                value = getattr(self, attr_name)
                # Don't copy methods
                if not callable(value):
                    try:
                        setattr(duplicate, attr_name, copy.copy(value))
                    except:
                        # If copy fails, try direct assignment
                        try:
                            setattr(duplicate, attr_name, value)
                        except:
                            pass
            except (AttributeError, TypeError):
                pass
        
        # Ensure dicts is copied properly
        if hasattr(self, 'dicts'):
            duplicate.dicts = self.dicts[:]
        
        return duplicate
    except Exception as e:
        print(f"Warning in patched_copy: {e}")
        # Fallback
        duplicate = self.__class__()
        if hasattr(self, 'dicts'):
            duplicate.dicts = self.dicts[:]
        return duplicate

# Apply the patch
django.template.context.Context.__copy__ = patched_copy
django.template.context.RequestContext.__copy__ = patched_copy

print("✅ Admin fix applied for Python 3.14!")