from dateutil.relativedelta import relativedelta
from saplogin import SAPLogin
from Minio import MinioConnector
import datetime
import json
import time
import os
sap = SAPLogin()

def f(num):
    """Função f() normaliza os números em formato texto"""
    return f"0{num}" if num < 10 else str(num)

def engdds_gl_accounts_main():
    
    # Instanciando o Minio para utilizar buffer e uploader a partir dos arquivos do json
    minio = MinioConnector()
    with open('files.json','rb') as file:
        meta_arquivos = json.load(file)
    
    # Ano Fiscal: 2025
    try:
        
        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass
        
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZFI_GL_PIVB"
        session.findById("wnd[0]").sendVKey(0)        
        session.findById("wnd[0]/tbar[1]/btn[17]").press()
        session.findById("wnd[1]/usr/txtV-LOW").text = "/GLACCOUNT_SUM"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/txtSO_GJAHR-LOW").text = "2025"
        session.findById("wnd[0]/usr/ctxtSO_BUDAT-LOW").text = "01.01.2025"
        session.findById("wnd[0]/usr/ctxtSO_BUDAT-HIGH").text = "31.12.2025"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except:
            pass
    
        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
            session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
            session.findById("wnd[0]").sendVKey(0) 

            # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
            # folder_path = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\04 - Data Dump\_stage"                   
            folder_path = meta_arquivos['engdds_gl_accounts.py']['path']
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = folder_path
            nome_arquivo = f"{meta_arquivos['engdds_gl_accounts.py']['files'][0]}"
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        time.sleep(5)
        # arquivo = minio.buffer_creator(meta_arquivos['engdds_gl_accounts.py']['path'][0], nome_arquivo)
        arquivo = minio.buffer_creator(folder_path, nome_arquivo)
        minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)
        sap.cleanup()

    except Exception as e:
        print(f'Erro ao exportar dados do relatório ZFI_GL_PIVB para 2025 :: {str(e)}')
        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.cleanup()

    # Ano Fiscal: 2026
    try:
        
        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass
        
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZFI_GL_PIVB"
        session.findById("wnd[0]").sendVKey(0)        
        session.findById("wnd[0]/tbar[1]/btn[17]").press()
        session.findById("wnd[1]/usr/txtV-LOW").text = "/GLACCOUNT_SUM"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/txtSO_GJAHR-LOW").text = "2026"
        session.findById("wnd[0]/usr/ctxtSO_BUDAT-LOW").text = "01.01.2026"
        session.findById("wnd[0]/usr/ctxtSO_BUDAT-HIGH").text = "31.12.2026"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except:
            pass
    
        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
            session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
            session.findById("wnd[0]").sendVKey(0) 

            # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #folder_path = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\04 - Data Dump\_stage"                   
            folder_path = meta_arquivos['engdds_gl_accounts.py']['path']
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = folder_path
            nome_arquivo = f"{meta_arquivos['engdds_gl_accounts.py']['files'][1]}"
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        time.sleep(5)
        # arquivo = minio.buffer_creator(meta_arquivos['engdds_gl_accounts.py']['path'][0], nome_arquivo)
        arquivo = minio.buffer_creator(folder_path, nome_arquivo)
        minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)
        sap.cleanup()

    except Exception as e:
        print(f'Erro ao exportar dados do relatório ZFI_GL_PIVB para 2026 :: {str(e)}')
        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.cleanup()

    time.sleep(2)


if __name__ == "__main__":
    engdds_gl_accounts_main()
