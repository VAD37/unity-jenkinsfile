import os,sys,inspect
currentFile = os.path.abspath(inspect.getfile(inspect.currentframe()))
currentdir = os.path.dirname(currentFile)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import Config

print("Run file: " + currentFile)
Config.print_all_config()


