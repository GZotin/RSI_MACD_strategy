import time
import win32api
import ctypes
import sys
from keys import API_key,secret_key
from binance.client import Client

client = Client(API_key,secret_key)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if is_admin():
    
    gt = client.get_server_time()
    tt = time.gmtime(int((gt["serverTime"])/1000))
    win32api.SetSystemTime(tt[0],tt[1],0,tt[2],tt[3],tt[4],tt[5],0)
    
else:
    # Re-run the program with admin rights
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

