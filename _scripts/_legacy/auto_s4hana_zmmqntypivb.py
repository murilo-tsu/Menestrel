# Importando bibliotecas relevantes
import win32com.client
import datetime
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

# Encerrar sessão caso haja alguma aberta
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im cmd.exe')
os.system('taskkill /f /im notepad.exe')

# E600 - ECFTO
saplogin()

# Definindo datas dinâmicas
now = time.localtime()
start_date = "01.01.2025"
#end_day = now.day
end_day = now.tm_mday
if end_day>=10:
    end_day = str(end_day)
else:
    end_day = '0' + str(end_day)

#end_month = now.month
end_month = now.tm_mon
if end_month >= 10:
    end_month = str(end_month)
else:
    end_month = '0' + str(end_month)

#end_year = now.year
end_year = now.tm_year

session.findById("wnd[0]").maximize()
session.findById("wnd[0]/tbar[0]/okcd").text = "ZMM_QNTY_PIVB"
session.findById("wnd[0]").sendVKey (0)
session.findById("wnd[0]/usr/ctxtSO_BUKRS-LOW").text = "E600"
session.findById("wnd[0]/usr/ctxtSO_BUDAT-LOW").text = start_date
session.findById("wnd[0]/usr/ctxtSO_BUDAT-HIGH").text = f"{end_day}.{end_month}.{end_year}"
session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "ZSOP"
session.findById("wnd[0]/usr/ctxtP_DISVAR").setFocus()
session.findById("wnd[0]/usr/ctxtP_DISVAR").caretPosition = 4
session.findById("wnd[0]/tbar[1]/btn[8]").press()
session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("TECHNAM")
session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\02 - Data Analytics\E600 Eurochem Fertilizantes Tocantins\E600 ECFTO - Estoque\SAP S4 HANA"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = f"{end_year}-{end_month}-{end_day} ZMM_QNTY_PIVB_E600.XLSX"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
session.findById("wnd[1]/tbar[0]/btn[11]").press()

# Encerrar sessão do SAP
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im cmd.exe')
os.system('taskkill /f /im notepad.exe')

# E890 - CMISS
saplogin()

session.findById("wnd[0]").maximize()
session.findById("wnd[0]/tbar[0]/okcd").text = "ZMM_QNTY_PIVB"
session.findById("wnd[0]").sendVKey (0)
session.findById("wnd[0]/usr/ctxtSO_BUKRS-LOW").text = "E890"
session.findById("wnd[0]/usr/ctxtSO_BUDAT-LOW").text = start_date
session.findById("wnd[0]/usr/ctxtSO_BUDAT-HIGH").text = f"{end_day}.{end_month}.{end_year}"
session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "ZSOP"
session.findById("wnd[0]/usr/ctxtP_DISVAR").setFocus()
session.findById("wnd[0]/usr/ctxtP_DISVAR").caretPosition = 4
session.findById("wnd[0]/tbar[1]/btn[8]").press()
session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("TECHNAM")
session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\02 - Data Analytics\E890 Eurochem Complexo Serra do Salitre\E890 CMISS - Estoque\SAP S4 HANA"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = f"{end_year}-{end_month}-{end_day} ZMM_QNTY_PIVB_E890.XLSX"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
session.findById("wnd[1]/tbar[0]/btn[11]").press()

# Encerrar sessão do SAP
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im cmd.exe')
os.system('taskkill /f /im notepad.exe')

# Em trânsito
saplogin()

session.findById("wnd[0]").maximize()
session.findById("wnd[0]/tbar[0]/okcd").text = "ZMB5T"
session.findById("wnd[0]").sendVKey(0)
session.findById("wnd[0]/usr/ctxtP_ALVDEF").text = "/Z2"
session.findById("wnd[0]/usr/ctxtP_ALVDEF").setFocus()
session.findById("wnd[0]/usr/ctxtP_ALVDEF").caretPosition = 3
session.findById("wnd[0]").sendVKey (0)
session.findById("wnd[0]").sendVKey (0)
session.findById("wnd[0]").sendVKey (8)
session.findById("wnd[0]/tbar[1]/btn[43]").press()
session.findById("wnd[0]/mbar/menu[3]/menu[2]/menu[1]").select()
session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").clickCurrentCell()
session.findById("wnd[0]/mbar/menu[0]/menu[1]/menu[1]").select()
session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\02 - Data Analytics\E600 Eurochem Fertilizantes Tocantins\E600 ECFTO - Trânsito de Materiais\SAP S4 HANA"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = f"{end_year}-{end_month}-{end_day} ZMB5T.XLSX"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 21
session.findById("wnd[1]/tbar[0]/btn[11]").press()

# Encerrar sessão do SAP
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im cmd.exe')
os.system('taskkill /f /im notepad.exe')