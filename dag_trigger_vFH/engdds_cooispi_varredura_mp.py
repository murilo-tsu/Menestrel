#Extração de dados do relatório COOISPI_VARREDURA do SAP S/4HANA para o MinIO - TRW

from saplogin import SAPLogin
from datetime import date, timedelta
from Minio import MinioConnector
import pandas as pd
import json
import time
import os
import datetime

data_fim = datetime.date.today()
data_inicio = data_fim - datetime.timedelta(days=30)

data_inicio_formatada = data_inicio.strftime("%d.%m.%Y")
data_fim_formatada = data_fim.strftime("%d.%m.%Y")

def f(num):

    return f"0{num}" if num < 10 else str(num)

# Instaciador de SAP Session
sap = SAPLogin()

def engdds_cooispi_varredura_mp_main():
    
    minio = MinioConnector()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, 'files.json')
    
    with open(files_json_path, 'r', encoding='utf-8') as file:
        meta_arquivos = json.load(file)
    
    #Login no SAP PT
    session = sap.login_to_s4hana_pt()
    
    try:
        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        now = time.localtime()  
        session.findById("wnd[0]/tbar[0]/okcd").Text = "/ncooispi"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ssub%_SUBSCREEN_TOPBLOCK:PPIO_ENTRY:1100/cmbPPIO_ENTRY_SC1100-PPIO_LISTTYP").Key = "PPIOM000"
        session.findById("wnd[0]/usr/ssub%_SUBSCREEN_TOPBLOCK:PPIO_ENTRY:1100/ctxtPPIO_ENTRY_SC1100-ALV_VARIANT").Text = "/PCPDADOSVAR"
        session.findById("wnd[0]/usr/tabsTABSTRIP_SELBLOCK/tabpSEL_00/ssub%_SUBSCREEN_SELBLOCK:PPIO_ENTRY:1200/ctxtS_AUART-LOW").Text = "zvar"
        session.findById("wnd[0]/usr/tabsTABSTRIP_SELBLOCK/tabpSEL_00/ssub%_SUBSCREEN_SELBLOCK:PPIO_ENTRY:1200/ctxtS_WERKS-LOW").text = "E90*"
        # session.findById("wnd[0]/usr/tabsTABSTRIP_SELBLOCK/tabpSEL_00/ssub%_SUBSCREEN_SELBLOCK:PPIO_ENTRY:1200/ctxtS_ECKST-LOW").text = data_inicio_formatada
        # session.findById("wnd[0]/usr/tabsTABSTRIP_SELBLOCK/tabpSEL_00/ssub%_SUBSCREEN_SELBLOCK:PPIO_ENTRY:1200/ctxtS_ECKST-HIGH").text = data_fim_formatada
        session.findById("wnd[0]/usr/tabsTABSTRIP_SELBLOCK/tabpSEL_00/ssub%_SUBSCREEN_SELBLOCK:PPIO_ENTRY:1200/ctxtS_AUART-LOW").SetFocus()
        session.findById("wnd[0]/usr/tabsTABSTRIP_SELBLOCK/tabpSEL_00/ssub%_SUBSCREEN_SELBLOCK:PPIO_ENTRY:1200/ctxtS_AUART-LOW").caretPosition = 4
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        session.findById("wnd[0]/usr/cntlCUSTOM/shellcont/shell/shellcont/shell").pressToolbarButton ("&NAVIGATION_PROFILE_TOOLBAR_EXPAND")
        session.findById("wnd[0]/usr/cntlCUSTOM/shellcont/shell/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
        session.findById("wnd[0]/usr/cntlCUSTOM/shellcont/shell/shellcont/shell").selectContextMenuItem ("&XXL")
        session.findById("wnd[1]/tbar[0]/btn[0]").press()

        #Nome do arquivo e caminho onde será salvo temporariamente
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_estoque.py']['path'][4]
        nome_arquivo = f"{now.tm_year}_{meta_arquivos['engdds_estoque.py']['files'][7]}"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        session.findById("wnd[0]/tbar[0]/okcd").Text = "/nex"
        session.findById("wnd[0]").sendVKey (0)

        arquivo = minio.buffer_creator(meta_arquivos['engdds_estoque.py']['path'][4], nome_arquivo)
        minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)

        # Encerrar sessão do SAP
        sap.encerrar_sap()
        # sap.limpar_processos()
        # sap.cleanup()

    except Exception as e:
        print(f'Erro ao exportar dados do relatório COOISPI_VARREDURA_MP :: {str(e)}')
        # Encerrar sessão do SAP
        sap.encerrar_sap()
        # sap.limpar_processos()
        # sap.cleanup()

    time.sleep(10)
if __name__ == "__main__":
    engdds_cooispi_varredura_mp_main()