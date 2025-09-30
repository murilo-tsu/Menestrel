import pandas as pd
import datetime
from datetime import date
import time
import win32com.client
import sys
import os
import subprocess
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
        session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = "@Himura2025s4hana"
        #session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = "EurochemFevereiro_2025"
        session.findById("wnd[0]").sendVKey(0)

    except:
        print(sys.exc_info()[0])
    
    #finally:
    #    session = None
    #    connection = None
    #    application = None
    #    SapGuiAuto = None

#saplogin()

def get_zsd00029(data):

    saplogin()
    session.findById("wnd[0]").maximize()
    session.findById("wnd[0]/tbar[0]/okcd").text = "ZSD00029"
    session.findById("wnd[0]").sendVKey (0)

    # Determinando a data final
    #data_final = data + pd.DateOffset(days = 7)
    data_final = data + pd.offsets.MonthEnd(0)
    data_final = data_final.date()

    # MES INICIAL -> STRING
    i_strmes = data.month
    if i_strmes >= 10:
        i_strmes = str(i_strmes)
    else:
        i_strmes = '0' + str(i_strmes)
    # DIA INICIAL -> STRING
    i_strdia = data.day
    if i_strdia >= 10:
        i_strdia = str(i_strdia)
    else:
        i_strdia = '0' + str(i_strdia)

    # MES FINAL -> STRING
    f_strmes = data_final.month
    if f_strmes >= 10:
        f_strmes = str(f_strmes)
    else:
        f_strmes = '0' + str(f_strmes)
    # DIA FINAL -> STRING
    f_strdia = data_final.day
    if f_strdia >= 10:
        f_strdia = str(f_strdia)
    else: 
        f_strdia = '0' + str(f_strdia)   

    # Declara a data inicial do relatório
    session.findById("wnd[0]/usr/ctxtS_ERDAT-LOW").text = f"{data.day}.{data.month}.{data.year}"
    # Declara a data final do relatório
    
    session.findById("wnd[0]/usr/ctxtS_ERDAT-HIGH").text = f"{data_final.day}.{data_final.month}.{data_final.year}"
    session.findById("wnd[0]/usr/ctxtS_WERKS-LOW").text = "*"
    session.findById("wnd[0]/usr/ctxtS_VKORG-LOW").text = "GE01"
    session.findById("wnd[0]/usr/ctxtS_VKORG-HIGH").text = "GE99"
    session.findById("wnd[0]/usr/ctxtP_VARIA").text = "//DATANLT"
    session.findById("wnd[0]/usr/chkP_EXFTO").setFocus()
    session.findById("wnd[0]/tbar[1]/btn[8]").press()
    session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select()
    session.findById("wnd[1]/tbar[0]/btn[0]").press()
    session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP ECC"
    # Alterando o nome do arquivo extraído

    session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = f"SAPECC_ZSD00029_{data.year}-{i_strmes}-{i_strdia}_{data_final.year}-{f_strmes}-{f_strdia}.txt"
    # Nome do arquivo abaixo utilizado para quando for necessário realizar
    # uma extração pontual da ZSD00029 com parâmetros customizados
    # session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "ZSD00029 - 2024 - 08.txt"
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 12
    session.findById("wnd[1]/tbar[0]/btn[11]").press()

    # Encerrar sessão do SAP
    os.system('taskkill /f /im saplogon.exe')

    # Recalcula nova data inicial

    print(f'Gerado relatório: ')
    print(f'DE: {data.year}-{data.month}-{data.day}')
    print(f'ATÉ: {data_final.year}-{data_final.month}-{data_final.day}')
    data = data_final + pd.DateOffset(days=1)
    print(f'Nova data inicial: {data.year}-{data.month}-{data.day}')
    return data

data = date(2025,5,1)
fim = date(2025,5,21)

while data <= fim:
    try:
        data = get_zsd00029(data)
        data = data.date()
    except Exception as e:
        print(f'Erro: {str(e)}')
        os.system('taskkill /f /im saplogon.exe')
        continue