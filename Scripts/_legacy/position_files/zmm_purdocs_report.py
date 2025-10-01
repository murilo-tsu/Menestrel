from saplogin import SAPLogin
from datetime import date, timedelta
import time
import os
sap = SAPLogin()

def f(num):
    """Função f() normaliza os números em formato texto"""
    return f"0{num}" if num < 10 else str(num)

session = sap.login_to_s4hana()

t_code = "ZMM_PURDOCS_REPORT"
folder_path = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\04 - Data Dump\_stage_position"
dt = date.today()
file_name = "EXPORT_" + t_code + "_SUPPLY_" + f(dt.day) + "." + f(dt.month) + "_FTO_FH.XLSX"
dt_criteria = f(dt.day) + "." + f(dt.month) + "." + f(dt.year)

session.findById("wnd[0]/tbar[0]/okcd").text = t_code
session.findById("wnd[0]").sendVKey (0)
session.findById("wnd[0]/usr/ctxtP_LAYOUT").text = "/SUPPLY"
session.findById("wnd[0]/tbar[1]/btn[8]").press()

try:
    session.findById("wnd[1]/usr/btnBUTTON_1").press()
except:
    pass

session.findById("wnd[0]/usr/cntlGRID/shellcont/shell/shellcont[0]/shell/shellcont[1]/shell").pressButton ("&XXL")
session.findById("wnd[1]/usr/ctxtDY_PATH").text = folder_path
session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = file_name
session.findById("wnd[1]/tbar[0]/btn[11]").press()
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im cmd.exe')
os.system('taskkill /f /im notepad.exe')