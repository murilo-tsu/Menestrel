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
        session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = "@Himura2024saphana"
        session.findById("wnd[0]").sendVKey(0)

    except:
        print(sys.exc_info()[0])
    
    #finally:
    #    session = None
    #    connection = None
    #    application = None
    #    SapGuiAuto = None

saplogin()
#Obter MB52
session.findById("wnd[0]").maximize()
session.findById("wnd[0]/tbar[0]/okcd").text = "MB52"
session.findById("wnd[0]").sendVKey (0)
session.findById("wnd[0]/usr/ctxtMATNR-LOW").text = "*"
session.findById("wnd[0]/usr/ctxtWERKS-LOW").text = "E89A"
session.findById("wnd[0]/usr/ctxtWERKS-HIGH").text = "E89Z"
session.findById("wnd[0]/usr/ctxtLGORT-LOW").text = "*"
session.findById("wnd[0]/usr/ctxtP_VARI").text = "//PCPSALITRE"
session.findById("wnd[0]/usr/ctxtP_VARI").setFocus()
session.findById("wnd[0]/usr/ctxtP_VARI").caretPosition = 12
session.findById("wnd[0]/tbar[1]/btn[8]").press()
session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select()
session.findById("wnd[1]/tbar[0]/btn[0]").press()
session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\02 - Data Analytics\E890 Eurochem Complexo Serra do Salitre\E890 CMISS - Estoque"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "MB52.txt"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 8
session.findById("wnd[1]/tbar[0]/btn[11]").press()

# Encerrar sessão do SAP
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im cmd.exe')