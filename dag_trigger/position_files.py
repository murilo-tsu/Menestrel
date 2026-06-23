from saplogin import SAPLogin
from Minio import MinioConnector
from datetime import date, timedelta
import shutil
import time
import json
import os
sap = SAPLogin()

def f(num):
    """Função f() normaliza os números em formato texto"""
    return f"0{num}" if num < 10 else str(num)

def position_files_main():
    # ::::::::::::::::::::::::::::::::::::::::
    # :: MB52 - ESTOQUE
    # ::::::::::::::::::::::::::::::::::::::::

    minio = MinioConnector()
    with open('files.json', 'r') as file:
        meta_arquivos = json.load(file)

    session = sap.login_to_s4hana(lang="PT")
    try:
        session.FindById("wnd[0]").SendVKey (0)
    except Exception as erro:
        print(erro)
        pass
    t_code = "MB52"
    # folder_path = r"C/Users/murilo.ribeiro/Desktop/tmpHANA/SAP4HANA/Position"
    dt = date.today() - timedelta(days=1)
    file_name = "EXPORT_" + t_code + "_EM_TRANSITO_" + f(dt.day) + "." + f(dt.month) + "_FTO_FH.XLSX"

    session.findById("wnd[0]/tbar[0]/okcd").text = t_code
    session.FindById("wnd[0]").SendVKey (0)

    session.findById("wnd[0]/usr/btn%_MATNR_%_APP_%-VALU_PUSH").press()
    session.findById("wnd[1]/tbar[0]/btn[16]").press()
    session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpINTL").select()
    session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpINTL/ssubSCREEN_HEADER:SAPLALDB:3020/tblSAPLALDBINTERVAL/ctxtRSCSEL_255-ILOW_I[1,0]").text = "1000000000"
    session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpINTL/ssubSCREEN_HEADER:SAPLALDB:3020/tblSAPLALDBINTERVAL/ctxtRSCSEL_255-IHIGH_I[2,0]").text = "2999999999"
    session.findById("wnd[1]/tbar[0]/btn[8]").press()

    session.FindById("wnd[0]/usr/btn%_WERKS_%_APP_%-VALU_PUSH").press()
    session.FindById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").Text = "*60*"
    session.FindById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").Text = "*90*"
    session.FindById("wnd[1]/tbar[0]/btn[8]").press()
    session.findById("wnd[0]/usr/radPA_FLT").select()
    session.findById("wnd[0]/usr/ctxtP_VARI").text = "/SUPPLY"
    session.findById("wnd[0]").sendVKey (8)
    sap.kill_excel()
    with sap.export_watchdog(180):
        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()
        session.findById("wnd[1]/tbar[0]/btn[0]").press()

        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # session.findById("wnd[2]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['position_files.py']['path']
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = file_name
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

    sap.limpar_processos()
    sap.cleanup()
    time.sleep(5)

    try:
        # filepath_destino = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\04 - Data Dump\_stage_position"
        filepath_destino = r"C:\Users\plandemand.svc\EUROCHEM FERTILIZANTES TOCANTINS\Suprimentos - FH"
        # filepath_origem = r"C:\Users\murilo.ribeiro\Desktop\tmpHANA\SAP4HANA\Position"
        filepath_origem = meta_arquivos['position_files.py']['path']
        shutil.copy2(filepath_origem+'/'+file_name, filepath_destino+'/'+ file_name)
    except:
        pass

    arquivo = minio.buffer_creator(meta_arquivos['position_files.py']['path'], file_name)
    minio.upload_from_bytesIO(arquivo,'tmp',file_name)

    # ::::::::::::::::::::::::::::::::::::::::
    # :: ZMM_QNTY_PIVB
    # ::::::::::::::::::::::::::::::::::::::::

    session = sap.login_to_s4hana(lang="PT")
    try:
        session.FindById("wnd[0]").SendVKey (0)
    except Exception as erro:
        print(erro)
        pass
    t_code = "ZMM_QNTY_PIVB"
    dt = date.today() - timedelta(days=1)
    file_name = "EXPORT_" + t_code + "_SUPPLY_" + f(dt.day) + "." + f(dt.month) + "_FTO_FH.XLSX"
    dt_criteria = f(dt.day) + "." + f(dt.month) + "." + f(dt.year)

    session.FindById("wnd[0]/tbar[0]/okcd").text = t_code
    session.FindById("wnd[0]").SendVKey (0)
    session.FindById("wnd[0]/usr/btn%_SO_BUKRS_%_APP_%-VALU_PUSH").press()
    session.FindById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "E600"
    session.FindById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "E900"
    session.FindById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").setFocus()
    session.FindById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").caretPosition = 4
    session.FindById("wnd[1]/tbar[0]/btn[8]").press()
    session.FindById("wnd[0]/usr/ctxtSO_BUDAT-LOW").text = dt_criteria
    session.FindById("wnd[0]/usr/ctxtSO_BUDAT-HIGH").text = dt_criteria
    session.FindById("wnd[0]/usr/ctxtP_DISVAR").text = "/SUPPLY"
    session.FindById("wnd[0]/usr/ctxtP_DISVAR").setFocus
    session.FindById("wnd[0]/usr/ctxtP_DISVAR").caretPosition = 6
    session.FindById("wnd[0]/tbar[1]/btn[8]").press()

    try:
        session.findById("wnd[1]/usr/btnBUTTON_1").press()
    except:
        pass

    session.FindById("wnd[0]/usr/tabsTABSTRIP/tabpTAB3/ssubSUB3:SAPLPIVB:1030/cntlCCONTROL_ACTIONS/shellcont/shell/shellcont[1]/shell[1]").hierarchyHeaderWidth = 899
    session.FindById("wnd[0]/usr/tabsTABSTRIP/tabpTAB3/ssubSUB3:SAPLPIVB:1030/cntlCCONTROL_ACTIONS/shellcont/shell/shellcont[1]/shell[1]").topNode = "          1"
    session.FindById("wnd[0]/shellcont/shell").setCurrentCell (2, "BSX_RACCT")
    session.FindById("wnd[0]/shellcont/shell").selectedRows = "2"
    session.FindById("wnd[0]/shellcont/shell").contextMenu()
    sap.kill_excel()
    with sap.export_watchdog(180):
        session.FindById("wnd[0]/shellcont/shell").SelectContextMenuItem ("&XXL")
        session.FindById("wnd[1]/usr/chkCB_ALWAYS").setFocus()
        session.FindById("wnd[1]/usr/chkCB_ALWAYS").selected = True
        session.FindById("wnd[1]/tbar[0]/btn[0]").press()

        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # session.findById("wnd[2]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['position_files.py']['path']
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = file_name
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

    sap.limpar_processos()
    sap.cleanup()
    time.sleep(5)

    try:
        # filepath_destino = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\04 - Data Dump\_stage_position"
        filepath_destino = r"C:\Users\plandemand.svc\EUROCHEM FERTILIZANTES TOCANTINS\Suprimentos - FH"
        # filepath_origem = r"C:\Users\murilo.ribeiro\Desktop\tmpHANA\SAP4HANA\Position"
        filepath_origem = meta_arquivos['position_files.py']['path']
        shutil.copy2(filepath_origem+'/'+file_name, filepath_destino+'/'+ file_name)
    except:
        pass

    arquivo = minio.buffer_creator(meta_arquivos['position_files.py']['path'], file_name)
    minio.upload_from_bytesIO(arquivo,'tmp',file_name)

    # ::::::::::::::::::::::::::::::::::::::::
    # :: ZMM_PURDOCS_REPORT
    # ::::::::::::::::::::::::::::::::::::::::

    session = sap.login_to_s4hana(lang="PT")
    try:
        session.FindById("wnd[0]").SendVKey (0)
    except Exception as erro:
        print(erro)
        pass
    t_code = "ZMM_PURDOCS_REPORT"
    dt = date.today() - timedelta(days=1)
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

    sap.kill_excel()
    with sap.export_watchdog(180):
        session.findById("wnd[0]/usr/cntlGRID/shellcont/shell/shellcont[0]/shell/shellcont[1]/shell").pressButton ("&XXL")
        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # session.findById("wnd[2]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['position_files.py']['path']
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = file_name
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

    sap.limpar_processos()
    sap.cleanup()
    time.sleep(5)

    try:
        # filepath_destino = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\04 - Data Dump\_stage_position"
        filepath_destino = r"C:\Users\plandemand.svc\EUROCHEM FERTILIZANTES TOCANTINS\Suprimentos - FH"
        # filepath_origem = r"C:\Users\murilo.ribeiro\Desktop\tmpHANA\SAP4HANA\Position"
        filepath_origem = meta_arquivos['position_files.py']['path']
        shutil.copy2(filepath_origem+'/'+file_name, filepath_destino+'/'+ file_name)
    except:
        pass

    arquivo = minio.buffer_creator(meta_arquivos['position_files.py']['path'], file_name)
    minio.upload_from_bytesIO(arquivo,'tmp',file_name)

if __name__ == "__main__":
    position_files_main()