from saplogin import SAPLogin
from Minio import MinioConnector
import datetime
import json
import time
import os
sap = SAPLogin()

def engdds_indirect_procurement_main():

    minio = MinioConnector()
    with open('files.json', 'rb') as file:
        meta_arquivos = json.load(file)


    # RELATÓRIO 1: ME5A ---------------------------------------------------------------------------------------------------------------------------------------------------------
    try:
        
        session = sap.login_to_s4hana(lang="PT")

        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass  

        session.findById("wnd[0]/tbar[0]/okcd").text = "ME5A"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/tbar[1]/btn[17]").press()
        session.findById("wnd[1]/usr/txtV-LOW").text = "/EUROCHEMBI26"
        session.findById("wnd[1]/usr/txtENAME-LOW").text = ""
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/tbar[1]/btn[33]").press()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").currentCellRow = -1
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").selectColumn ("VARIANT")
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").selectedRows = ""
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").contextMenu()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").selectContextMenuItem ("&FILTER")
        session.findById("wnd[2]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").text = "/EUROCHEMRC"
        session.findById("wnd[2]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").caretPosition = 11
        session.findById("wnd[2]/tbar[0]/btn[0]").press()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").clickCurrentCell()
        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()
        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except:
            pass

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_indirect_procurement.py']['path']
        nome_arquivo = f"{meta_arquivos['engdds_indirect_procurement.py']['files'][0]}"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()

        # Gravar no MinIO
        arquivo = minio.buffer_creator(meta_arquivos['engdds_indirect_procurement.py']['path'],nome_arquivo)
        minio.upload_from_bytesIO(arquivo,'tmp',nome_arquivo)
        sap.cleanup()

    except Exception as erro:
        print(f'Erro ao exportar dados do relatório ME5A = {erro}')
        sap.limpar_processos()
        sap.cleanup()

    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------
    # RELATÓRIO 2: ME2L ---------------------------------------------------------------------------------------------------------------------------------------------
    try:

        session = sap.login_to_s4hana(lang="PT")

        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass  

        session.findById("wnd[0]/tbar[0]/okcd").text = "ME2L"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/tbar[1]/btn[17]").press()
        session.findById("wnd[1]/usr/txtV-LOW").text = "/EUROCHEMBI26"
        session.findById("wnd[1]/usr/txtENAME-LOW").text = ""
        session.findById("wnd[1]/usr/txtV-LOW").caretPosition = 13
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        # session.findById("wnd[0]/usr/ctxtS_EBELN-LOW").text = "4500815559"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        # session.findById("wnd[0]/usr/ctxtS_EBELN-LOW").setFocus()
        # session.findById("wnd[0]/usr/ctxtS_EBELN-LOW").caretPosition = 10
        # session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/tbar[1]/btn[23]").press()

        # session.findById("wnd[0]/tbar[1]/btn[23]").press()
        session.findById("wnd[0]/tbar[1]/btn[33]").press()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").currentCellRow = -1
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").selectColumn ("VARIANT")
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").selectedRows = ""
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").contextMenu()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").selectContextMenuItem ("&FILTER")
        session.findById("wnd[2]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").text = "/COMPRASBI"
        session.findById("wnd[2]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").caretPosition = 11
        session.findById("wnd[2]/tbar[0]/btn[0]").press()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").clickCurrentCell()
        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()

        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except:
            pass

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_indirect_procurement.py']['path']
        nome_arquivo = f"{meta_arquivos['engdds_indirect_procurement.py']['files'][1]}"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()

        # Gravar no MinIO
        arquivo = minio.buffer_creator(meta_arquivos['engdds_indirect_procurement.py']['path'],nome_arquivo)
        minio.upload_from_bytesIO(arquivo,'tmp',nome_arquivo)
        sap.cleanup()

    except Exception as erro:
        print(f'Erro ao exportar dados do relatório ME2L = {erro}')
        sap.limpar_processos()
        sap.cleanup()
    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    # RELATÓRIO 3: ME3L ---------------------------------------------------------------------------------------------------------------------------------
    try:

        session = sap.login_to_s4hana(lang="PT")

        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass  

        session.findById("wnd[0]/tbar[0]/okcd").text = "ME3L"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtLISTU").text = "ALV"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/tbar[1]/btn[33]").press()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").currentCellRow = -1
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").selectColumn ("VARIANT")
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").selectedRows = ""
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").contextMenu()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").selectContextMenuItem ("&FILTER")
        session.findById("wnd[2]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").text = "/CONTRATOSBI"
        session.findById("wnd[2]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").caretPosition = 11
        session.findById("wnd[2]/tbar[0]/btn[0]").press()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").clickCurrentCell()

        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()
        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except:
            pass

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_indirect_procurement.py']['path']
        nome_arquivo = f"{meta_arquivos['engdds_indirect_procurement.py']['files'][2]}"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()

        # Gravar no MinIO
        arquivo = minio.buffer_creator(meta_arquivos['engdds_indirect_procurement.py']['path'],nome_arquivo)
        minio.upload_from_bytesIO(arquivo,'tmp',nome_arquivo)
        sap.cleanup()

    except Exception as erro:
        print(f'Erro ao exportar dados do relatório ME3L = {erro}')
        sap.limpar_processos()
        sap.cleanup()
    # ----------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    engdds_indirect_procurement_main()