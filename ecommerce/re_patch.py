import re 
 
original_findall = re.findall 
 
def safe_findall(pattern, string, flags=0): 
    try: 
        return original_findall(pattern, string, flags) 
    except RecursionError: 
        return [] 
 
re.findall = safe_findall 
print("? re.findall patch applied!") 
