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
    os.system("wget https://raw.githubusercontent.com/Manoj-Paramsetti/DockerCraft/main/requirements.txt")
    os.system("PIP_BREAK_SYSTEM_PACKAGES=1 python3 -m pip install -r requirements.txt")
    # Delete the requirements.txt file
    os.system("rm requirements.txt")
# save dockercraft file to /usr/bin
os.system("sudo wget -O /usr/local/bin/dockercraft https://raw.githubusercontent.com/Manoj-Paramsetti/DockerCraft/main/dockercraft.py && sudo chmod +x /usr/local/bin/dockercraft")
