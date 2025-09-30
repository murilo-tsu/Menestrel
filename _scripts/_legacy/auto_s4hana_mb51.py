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

        connection = application.OpenConnection(".SAP S/4 HANA PROD", True)
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

        session.findById("wnd[0]/usr/txtRSYST-BNAME").text = "MLRIBEIRO"
        session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = "@Himura2024sap"
        session.findById("wnd[0]").sendVKey(0)

    except:
        print(sys.exc_info()[0])
    
    #finally:
    #    session = None
    #    connection = None
    #    application = None
    #    SapGuiAuto = None

saplogin()
# Obter MB51
session.findById("wnd[0]").maximize()
session.findById("wnd[0]/tbar[0]/okcd").text = "mb51"
session.findById("wnd[0]").sendVKey (0)
session.findById("wnd[0]/tbar[1]/btn[17]").press()
session.findById("wnd[1]/tbar[0]/btn[8]").press()
session.findById("wnd[0]/usr/ctxtALV_DEF").setFocus()
session.findById("wnd[0]/usr/ctxtALV_DEF").caretPosition = 4
session.findById("wnd[0]").sendVKey (4)
session.findById("wnd[1]/usr").verticalScrollbar.position = 1
session.findById("wnd[1]/usr").verticalScrollbar.position = 2
session.findById("wnd[1]/usr").verticalScrollbar.position = 3
session.findById("wnd[1]/usr").verticalScrollbar.position = 4
session.findById("wnd[1]/usr").verticalScrollbar.position = 5
session.findById("wnd[1]/usr").verticalScrollbar.position = 4
session.findById("wnd[1]/usr").verticalScrollbar.position = 3
session.findById("wnd[1]/usr").verticalScrollbar.position = 2
session.findById("wnd[1]/usr/lbl[14,9]").setFocus()
session.findById("wnd[1]/usr/lbl[14,9]").caretPosition = 3
session.findById("wnd[1]/tbar[0]/btn[0]").press()
session.findById("wnd[0]/tbar[1]/btn[8]").press()
session.findById("wnd[0]/mbar/menu[0]/menu[1]/menu[2]").select()
session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select()
session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").setFocus()
session.findById("wnd[1]/tbar[0]/btn[0]").press()
session.findById("wnd[1]/usr/ctxtDY_PATH").setFocus()
session.findById("wnd[1]/usr/ctxtDY_PATH").caretPosition = 0
session.findById("wnd[1]").sendVKey (4)
session.findById("wnd[2]/usr/ctxtDY_PATH").setFocus()
session.findById("wnd[2]/usr/ctxtDY_PATH").caretPosition = 0
session.findById("wnd[2]").sendVKey (4)
session.findById("wnd[3]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\02 - Data Analytics\E890 Eurochem Complexo Serra do Salitre\E890 CMISS - Faturamento\MB51"
session.findById("wnd[3]/usr/ctxtDY_FILENAME").text = "MB51.txt"
session.findById("wnd[3]/usr/ctxtDY_PATH").setFocus()
session.findById("wnd[3]/usr/ctxtDY_PATH").caretPosition = 154
session.findById("wnd[3]/tbar[0]/btn[11]").press()
session.findById("wnd[2]/tbar[0]/btn[11]").press()
session.findById("wnd[1]/tbar[0]/btn[11]").press()

# Encerrar sessão do SAP
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im cmd.exe')