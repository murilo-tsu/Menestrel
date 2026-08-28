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

def engdds_custos_main():
    minio = MinioConnector()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, 'files.json')
    
    with open(files_json_path, 'r', encoding='utf-8') as file:  # Alterei 'rb' para 'r' e adicionei encoding
        meta_arquivos = json.load(file)
    
    end_year_custos = f(datetime.date.today().year)
    end_month_custos = f(datetime.date.today().month)
    end_day_custos = f(datetime.date.today().day)
    dt_custos = f"{end_day_custos}.{end_month_custos}.{end_year_custos}"
    dt_name_custos = f"{end_year_custos}-{end_month_custos}-{end_day_custos}"

    cost_comp = meta_arquivos['engdds_custos.py']['cost_comp']
    
    for key, value in cost_comp.items():
        nome_arquivo = dt_name_custos + " " + meta_arquivos['engdds_custos.py']['files'] + value
        try:
            session = sap.login_to_s4hana()
            try:
                session.FindById("wnd[0]").SendVKey (0)
            except:
                pass
            session.findById("wnd[0]").maximize()
            session.findById("wnd[0]/tbar[0]/okcd").text = "ZSD_RPLCMNT_COST"
            session.findById("wnd[0]").sendVKey (0)
            session.findById("wnd[0]/usr/ctxtS_LCOST-LOW").text = key

            session.findById("wnd[0]/usr/ctxtP_DATAB").text = dt_custos
            session.findById("wnd[0]").sendVKey (0)

            session.findById("wnd[0]/usr/btn%_S_VSTEL_%_APP_%-VALU_PUSH").press()
            session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/txtRSCSEL_255-SLOW_I[1,0]").text = "E90*"
            session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/txtRSCSEL_255-SLOW_I[1,1]").text = "P90*"
            session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/txtRSCSEL_255-SLOW_I[1,1]").setFocus()
            session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/txtRSCSEL_255-SLOW_I[1,1]").caretPosition = 4
            session.findById("wnd[1]/tbar[0]/btn[8]").press()

            session.findById("wnd[0]/tbar[1]/btn[8]").press()
            
            session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()
            session.findById("wnd[1]/tbar[0]/btn[0]").press()

            #print(f"{meta_arquivos['engdds_custos.py']['path']}/{nome_arquivo}")

            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_custos.py']['path']
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo

            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 36
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

            caminho_arquivo = meta_arquivos['engdds_custos.py']['path'] +"/"+nome_arquivo
            #print(f"ATUALIZADO: {caminho_arquivo}")

            arquivo = minio.buffer_creator(meta_arquivos['engdds_custos.py']['path'], nome_arquivo)
            minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)
            # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
            sap.encerrar_sap()

        
        except Exception as erro:
            print(f'Erro ao exportar dados do relatório ZSD_RPLCMNT_COST{value} :: {str(erro)}')

if __name__ == "__main__":
    engdds_custos_main()