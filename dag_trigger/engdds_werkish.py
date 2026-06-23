from saplogin import SAPLogin
from Minio import MinioConnector
import time
import json
import os
sap = SAPLogin()

def engdds_werkish_main():

    minio = MinioConnector()
    with open('files.json','rb') as file:
        meta_arquivos = json.load(file)

    # WERKS :: CADASTRO DE PLANTAS
    try:
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass

        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "ZVMM_WERKS_I"
        session.findById("wnd[0]/usr/ctxtGD-TAB").setFocus()
        session.findById("wnd[0]/usr/ctxtGD-TAB").caretPosition = 12
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem("&XXL")

            try:
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except:
                pass

            # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
            # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
            # session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_werkish.py']['path']
            # session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "WERKS.xlsx"
            nome_arquivo = meta_arquivos['engdds_werkish.py']['files'][0]
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # sap.upload_files(r"Shared Documents/Hadoop/SAP4HANA/Tabelas",
        #                  r"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/Tabelas/WERKS.xlsx")
        arquivo = minio.buffer_creator(meta_arquivos['engdds_werkish.py']['path'], nome_arquivo)
        minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)
        # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
        sap.cleanup()

    finally:
        # Always clean up
        sap.cleanup()

    # LGORT :: CADASTRO DE DEPÓSITOS
    try:
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass
        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "ZVMM_LGORT_2"
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").setFocus
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").caretPosition = 0
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem ("&XXL")

            try:
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except:
                pass

            # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
            # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
            # session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_werkish.py']['path']
            # session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "LGORT.xlsx"
            nome_arquivo = meta_arquivos['engdds_werkish.py']['files'][1]
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # sap.upload_files(r"Shared Documents/Hadoop/SAP4HANA/Tabelas",
        #                  r"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/Tabelas/LGORT.xlsx")
        arquivo = minio.buffer_creator(meta_arquivos['engdds_werkish.py']['path'], nome_arquivo)
        minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)
        # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
        sap.cleanup()


    except Exception as e:
        print(f'Erro ao exportar dados do relatório SE16N :: ZVMM_LGORT_2 :: {str(e)}')
        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.cleanup()

    # TVSTT :: Descrição de Shipping Points
    try:
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass
        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "TVSTT"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem ("&XXL")

            try:
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except:
                pass

            # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
            # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
            # session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_werkish.py']['path']
            # session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "TVSTT.xlsx"
            nome_arquivo = meta_arquivos['engdds_werkish.py']['files'][2]
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # sap.upload_files(r"Shared Documents/Hadoop/SAP4HANA/Tabelas",
        #                  r"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/Tabelas/TVSTT.xlsx")
        arquivo = minio.buffer_creator(meta_arquivos['engdds_werkish.py']['path'], nome_arquivo)
        minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        sap.cleanup()

    except Exception as e:
        print(f'Erro ao exportar dados do relatório SE16N :: TVSTT :: {str(e)}')
        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.cleanup()

    time.sleep(10)
    # sap.trigger_airflow_dag(dag_name="engdds_units")

if __name__ == "__main__":
    engdds_werkish_main()