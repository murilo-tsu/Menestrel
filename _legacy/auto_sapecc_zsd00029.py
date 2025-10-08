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

        connection = application.OpenConnection(".SAP ECC Heringer PROD", True)
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

        session.findById("wnd[0]/usr/txtRSYST-BNAME").text = "mribeiro.fto"
        #session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = "@Himura2025saphana"
        session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = "@Himura2025s4hana"
        session.findById("wnd[0]").sendVKey(0)

    except:
        print(sys.exc_info()[0])
    
    #finally:
    #    session = None
    #    connection = None
    #    application = None
    #    SapGuiAuto = None

saplogin()

# Definindo datas dinâminas
now = time.localtime()
start_date = datetime.datetime(now.tm_year,now.tm_mon,now.tm_mday) + datetime.timedelta(days=-30)
start_day = start_date.day
start_month = start_date.month
start_year = start_date.year
end_day = now.tm_mday
end_month = now.tm_mon
end_year = now.tm_year

session.findById("wnd[0]").maximize()
session.findById("wnd[0]/tbar[0]/okcd").text = "ZSD00029"
session.findById("wnd[0]").sendVKey (0)

# Data Inicial: 
session.findById("wnd[0]/usr/ctxtS_ERDAT-LOW").text = f"{start_day}.{start_month}.{start_year}"
#session.findById("wnd[0]/usr/ctxtS_ERDAT-LOW").text = "01.11.2024"
# Data Final:
session.findById("wnd[0]/usr/ctxtS_ERDAT-HIGH").text = f"{end_day}.{end_month}.{end_year}"
#session.findById("wnd[0]/usr/ctxtS_ERDAT-HIGH").text = "30.11.2024"

session.findById("wnd[0]/usr/ctxtS_WERKS-LOW").text = "*"
session.findById("wnd[0]/usr/ctxtS_VKORG-LOW").text = "GE01"
session.findById("wnd[0]/usr/ctxtS_VKORG-HIGH").text = "GE99"
session.findById("wnd[0]/usr/ctxtP_VARIA").text = "//DATANLT"
session.findById("wnd[0]/usr/chkP_EXFTO").setFocus()
session.findById("wnd[0]/tbar[1]/btn[8]").press()
session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select()
session.findById("wnd[1]/tbar[0]/btn[0]").press()
session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\02 - Data Analytics\E900 Eurochem Fertilizantes Heringer\E900 ECFHG - Faturamento\ZSD00029"

# Alterando o nome do arquivo extraído
session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "ZSD00029.txt"
# Nome do arquivo abaixo utilizado para quando for necessário realizar
# uma extração pontual da ZSD00029 com parâmetros customizados
# session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "ZSD00029 - 2024 - 08.txt"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 12
session.findById("wnd[1]/tbar[0]/btn[11]").press()

# Encerrar sessão do SAP
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im cmd.exe')