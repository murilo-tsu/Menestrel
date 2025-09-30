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

def saplogin_ecc():
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

# MARA TABLE
saplogin()

session.findById("wnd[0]").maximize()
session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
session.findById("wnd[0]").sendVKey (0)
session.findById("wnd[0]/usr/ctxtGD-TAB").text = "MARA"
session.findById("wnd[0]/usr/ctxtGD-TAB").caretPosition = 4
session.findById("wnd[0]").sendVKey (0)
session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
session.findById("wnd[0]").sendVKey (18)
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/chkGS_SELFIELDS-MARK[5,1]").selected = True
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/chkGS_SELFIELDS-MARK[5,2]").selected = True
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/chkGS_SELFIELDS-MARK[5,3]").selected = True
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").setFocus()
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").press()
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC").columns.elementAt(1).width = 31
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = "1000000000"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = "2000000000"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]").text = "4000000000"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,3]").text = "7000000000"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,0]").text = "1999999999"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,1]").text = "2999999999"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,2]").text = "4999999999"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").text = "7999999999"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").setFocus()
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").caretPosition = 10
session.findById("wnd[1]/tbar[0]/btn[8]").press()
session.findById("wnd[0]/tbar[1]/btn[8]").press()
session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem ("&XXL")
session.findById("wnd[1]/usr/ctxtDY_PATH").setFocus()
session.findById("wnd[1]/usr/ctxtDY_PATH").caretPosition = 0
session.findById("wnd[1]").sendVKey (4)
session.findById("wnd[2]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "MARA.XLSX"
session.findById("wnd[2]/usr/ctxtDY_FILENAME").caretPosition = 9
session.findById("wnd[2]/tbar[0]/btn[11]").press()
session.findById("wnd[1]/tbar[0]/btn[11]").press()
# Encerrar sessão do SAP
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im cmd.exe')
os.system('taskkill /f /im notepad.exe')

# MAKT TABLE
saplogin()
session.findById("wnd[0]").maximize()
session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
session.findById("wnd[0]").sendVKey (0)
session.findById("wnd[0]/usr/ctxtGD-TAB").text = "MAKT"
session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
session.findById("wnd[0]").sendVKey (18)
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").setFocus()
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").press()
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = "1000000000"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = "2000000000"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]").text = "4000000000"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,3]").text = "7000000000"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,0]").text = "1999999999"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,1]").text = "2999999999"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,2]").text = "4999999999"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").text = "7999999999"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").setFocus()
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").caretPosition = 10
session.findById("wnd[1]/tbar[0]/btn[8]").press()
session.findById("wnd[0]/tbar[1]/btn[8]").press()
session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").firstVisibleRow = 36
session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem ("&XXL")
session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "MAKT.XLSX"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
session.findById("wnd[1]/tbar[0]/btn[11]").press()
# Encerrar sessão do SAP
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im cmd.exe')
os.system('taskkill /f /im notepad.exe')

# ZVMM_MAT_CLASS TABLE
saplogin()
session.findById("wnd[0]").maximize()
session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
session.findById("wnd[0]").sendVKey (0)
session.findById("wnd[0]/usr/ctxtGD-TAB").text = "ZVMM_MAT_CLASS"
session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
session.findById("wnd[0]").sendVKey (18)
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").setFocus()
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").press()
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = "1000000000"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = "2000000000"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]").text = "4000000000"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,3]").text = "7000000000"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,0]").text = "1999999999"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,1]").text = "2999999999"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,2]").text = "4999999999"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").text = "7999999999"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").setFocus()
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").caretPosition = 10
session.findById("wnd[1]/tbar[0]/btn[8]").press()
session.findById("wnd[0]/tbar[1]/btn[8]").press()
session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").firstVisibleRow = 36
session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem ("&XXL")
session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "ZVMM_MAT_CLASS.XLSX"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
session.findById("wnd[1]/tbar[0]/btn[11]").press()
# Encerrar sessão do SAP
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im cmd.exe')
os.system('taskkill /f /im notepad.exe')

# MCHB TABLE
saplogin()
now = time.localtime()
session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
session.findById("wnd[0]").sendVKey (0)
session.findById("wnd[0]/usr/ctxtGD-TAB").text = "MCHB"
session.findById("wnd[0]").sendVKey (0)
session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
session.findById("wnd[0]/usr/txtGD-MAX_LINES").setFocus
session.findById("wnd[0]/usr/txtGD-MAX_LINES").caretPosition = 0
session.findById("wnd[0]").sendVKey (0)
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 1
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 2
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 3
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 4
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 5
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 6
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 7
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,3]").setFocus()
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,3]").press()
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = f"{now.tm_year}"
#session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = "2025"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").setFocus()
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").caretPosition = 4
session.findById("wnd[1]/tbar[0]/btn[8]").press()
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 8
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,3]").setFocus()
session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,3]").press()
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = f"{now.tm_mon}"
#session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = "2"
#session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]").text = "3"
#session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,3]").text = "4"
#session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,4]").text = "5"
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,4]").setFocus()
session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,4]").caretPosition = 1
session.findById("wnd[1]/tbar[0]/btn[8]").press()
session.findById("wnd[0]/tbar[1]/btn[8]").press()
session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem ("&XXL")
session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "MCHB.XLSX"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
session.findById("wnd[1]/tbar[0]/btn[11]").press()
# Encerrar sessão do SAP
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im cmd.exe')
os.system('taskkill /f /im notepad.exe')


# ZMM00252 - MATERIA-PRIMA
saplogin_ecc()
session.findById("wnd[0]").maximize()
session.findById("wnd[0]/tbar[0]/okcd").text = "ZMM00252"
session.findById("wnd[0]").sendVKey (0)
session.findById("wnd[0]/usr/btn%_S_MATNR_%_APP_%-VALU_PUSH").press()
session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpINTL").select()
session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpINTL/ssubSCREEN_HEADER:SAPLALDB:3020/tblSAPLALDBINTERVAL/ctxtRSCSEL-ILOW_I[1,0]").text = "10000000000000"
session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpINTL/ssubSCREEN_HEADER:SAPLALDB:3020/tblSAPLALDBINTERVAL/ctxtRSCSEL-IHIGH_I[2,0]").text = "19999999999999"
session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpINTL/ssubSCREEN_HEADER:SAPLALDB:3020/tblSAPLALDBINTERVAL/ctxtRSCSEL-ILOW_I[1,1]").setFocus
session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpINTL/ssubSCREEN_HEADER:SAPLALDB:3020/tblSAPLALDBINTERVAL/ctxtRSCSEL-ILOW_I[1,1]").caretPosition = 0
session.findById("wnd[1]/tbar[0]/btn[8]").press()
session.findById("wnd[0]/tbar[1]/btn[8]").press()
session.findById("wnd[0]/tbar[1]/btn[45]").press()
session.findById("wnd[1]/tbar[0]/btn[0]").press()
session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "ZMM00252.txt"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 12
session.findById("wnd[1]/tbar[0]/btn[0]").press()
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im saplogon.exe')
os.system('taskkill /f /im cmd.exe')
os.system('taskkill /f /im notepad.exe')