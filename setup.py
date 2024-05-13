import os
def check_imports():
    try:
        import curses
        import yaml
        import argparse
        return True
    except ImportError as e:
        return False
    
if check_imports():
    print("All imports are available")
else:
    os.system("wget https://raw.githubusercontent.com/AnshumanFauzdar/Python-CLI-App/main/requirements.txt")
    os.system("pip install -r requirements.txt --break-system-packages")
    # Delete the requirements.txt file
    os.system("rm requirements.txt")
    os.system("wget ")
