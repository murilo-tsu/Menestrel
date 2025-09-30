from saplogin import SAPLogin
from datetime import date, timedelta
import time
import os
sap = SAPLogin()

def f(num):
    """Função f() normaliza os números em formato texto"""
    return f"0{num}" if num < 10 else str(num)

session = sap.login_to_s4hana()
t_code = "MB52"
folder_path = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\04 - Data Dump\_stage_position"
dt = date.today()
file_name = "EXPORT_" + t_code + "_EM_TRANSITO_" + f(dt.day) + "." + f(dt.month) + "_FTO_FH.XLSX"

session.findById("wnd[0]/tbar[0]/okcd").text = t_code
session.FindById("wnd[0]").SendVKey (0)
session.FindById("wnd[0]/usr/btn%_WERKS_%_APP_%-VALU_PUSH").press()
session.FindById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").Text = "*60*"
session.FindById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").Text = "*90*"
session.FindById("wnd[1]/tbar[0]/btn[8]").press()
session.findById("wnd[0]/usr/radPA_FLT").select()
session.findById("wnd[0]/usr/ctxtP_VARI").text = "/SUPPLY"
session.findById("wnd[0]").sendVKey (8)
session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()
session.FindById("wnd[1]/usr/ctxtDY_PATH").text = folder_path
session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = file_name
session.findById("wnd[1]/tbar[0]/btn[11]").press()

os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im cmd.exe')
os.system('taskkill /f /im notepad.exe')
