# Importando bibliotecas relevantes
import win32com.client
import sys
import os
import subprocess
import time
import pyautogui
import mouse
import keyboard

# Função utilizada para abrir o GUI e realizar o login

def saplogin():
    global session
    try:

        #path = r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe"
        path = r"C:\Program Files\SAP\FrontEnd\SAPGUI\saplogon.exe"
        subprocess.Popen(path)
        time.sleep(10)

        SapGuiAuto = win32com.client.GetObject('SAPGUI')
        if not type(SapGuiAuto) == win32com.client.CDispatch:
            return

        application = SapGuiAuto.GetScriptingEngine
        if not type(application) == win32com.client.CDispatch:
            SapGuiAuto = None
            return

        connection = application.OpenConnection("SAP S/4 HANA PROD", True)
        #connection = application.OpenConnection("SAP S/4 HANA QAS", True)
        if not type(connection) == win32com.client.CDispatch: 
            application = None
            SapGuiAuto = None
            return

        # Nesse momento, é necessário executar um script paralelo para controlar
        # o mouse e realizar os clicks de login

        session = connection.Children(0)
        if not type(session) == win32com.client.CDispatch:
            connection = None
            application = None
            SapGuiAuto = None
            return

        session.findById("wnd[0]/usr/txtRSYST-BNAME").text = "U0000753"
        session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = "@Himura2025s4hana"
        session.findById("wnd[0]").sendVKey(0)

    except:
        print(sys.exc_info()[0])
    
    #finally:
    #    session = None
    #    connection = None
    #    application = None
    #    SapGuiAuto = None

# EMPRESA E600 - ECFTO
saplogin()

session.findById("wnd[0]").maximize()
session.findById("wnd[0]/tbar[0]/okcd").text = "ZSD_PIVB"
session.findById("wnd[0]").sendVKey (0)
session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "ZSOP"
session.findById("wnd[0]/usr/ctxtSO_VKORG-LOW").text = "E600"
session.findById("wnd[0]/usr/ctxtP_DISVAR").caretPosition = 4
session.findById("wnd[0]/tbar[1]/btn[8]").press()
session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("TECHNAM")
session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")

# Opção 1: usado para extrair um arquivo do tipo .txt
#session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&PC")
#session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select()
#session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").setFocus()
#session.findById("wnd[1]/tbar[0]/btn[0]").press()
#session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\02 - Data Analytics\E600 Eurochem Fertilizantes Tocantins\E600 ECFTO - Faturamento\SAP S4 HANA"
#session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "ZSD_PIVB_E600.txt"
#session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 12
#session.findById("wnd[1]/tbar[0]/btn[11]").press()

# Opção 2: usado para extrair um arquivo do tipo .xlsx
session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
session.findById("wnd[1]/tbar[0]/btn[0]").press()
session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Faturamento"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "ZSD_PIVB_E600.XLSX"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 18
session.findById("wnd[1]/tbar[0]/btn[11]").press()
session.findById("wnd[0]").close()

# Encerrar sessão do SAP
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im notepad.exe')
os.system('taskkill /f /im cmd.exe')

# EMPRESA E890 - ECFTO
saplogin()

session.findById("wnd[0]").maximize()
session.findById("wnd[0]/tbar[0]/okcd").text = "ZSD_PIVB"
session.findById("wnd[0]").sendVKey (0)
session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "ZSOP"
session.findById("wnd[0]/usr/ctxtSO_VKORG-LOW").text = "E890"
session.findById("wnd[0]/usr/ctxtP_DISVAR").caretPosition = 4
session.findById("wnd[0]/tbar[1]/btn[8]").press()
session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("TECHNAM")
session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")

# Opção 1: usado para extrair um arquivo do tipo .txt
#session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&PC")
#session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select()
#session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").setFocus()
#session.findById("wnd[1]/tbar[0]/btn[0]").press()
#session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\02 - Data Analytics\E600 Eurochem Fertilizantes Tocantins\E600 ECFTO - Faturamento\SAP S4 HANA"
#session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "ZSD_PIVB_E600.txt"
#session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 12
#session.findById("wnd[1]/tbar[0]/btn[11]").press()

# Opção 2: usado para extrair um arquivo do tipo .xlsx
session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
session.findById("wnd[1]/tbar[0]/btn[0]").press()
session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Faturamento"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "ZSD_PIVB_E890.XLSX"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 18
session.findById("wnd[1]/tbar[0]/btn[11]").press()
session.findById("wnd[0]").close()

# Encerrar sessão do SAP
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im notepad.exe')
os.system('taskkill /f /im cmd.exe')