from saplogin import SAPLogin
from datetime import date
from Minio import MinioConnector
import pandas as pd
import json
import time
import os
import logging


def f(num):
    return f"0{num}" if num < 10 else str(num)


# Instanciador de SAP Session
sap = SAPLogin()


def engdds_zfi_gl_pivb_main():
    logging.info("---- INICIANDO PROCESSO: ENGDDS_ZFI_GL_PIVB.PY ----")

    minio = MinioConnector()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, 'files.json')

    with open(files_json_path, 'r', encoding='utf-8') as file:
        meta_arquivos = json.load(file)

    # === Datas do mês anterior (M-1) ===
    hoje = date.today()
    primeiro_dia_mes_atual = hoje.replace(day=1)
    ultimo_dia_mes_anterior = primeiro_dia_mes_atual - pd.Timedelta(days=1)
    primeiro_dia_mes_anterior = ultimo_dia_mes_anterior.replace(day=1)

    dia_ini = f(primeiro_dia_mes_anterior.day)
    mes_ini = f(primeiro_dia_mes_anterior.month)
    ano_ini = str(primeiro_dia_mes_anterior.year)

    dia_fim = f(ultimo_dia_mes_anterior.day)
    mes_fim = f(ultimo_dia_mes_anterior.month)
    ano_fim = str(ultimo_dia_mes_anterior.year)

    session = sap.login_to_s4hana()

    try:
        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nZFI_GL_PIVB"
        session.findById("wnd[0]").sendVKey(0)

        session.findById("wnd[0]/usr/ctxtSO_RLDNR-LOW").text = "0L"
        session.findById("wnd[0]/usr/ctxtSO_BUKRS-LOW").text = "E900"
        session.findById("wnd[0]/usr/txtSO_GJAHR-LOW").text = ano_ini

        session.findById("wnd[0]/usr/ctxtSO_BUDAT-LOW").text = f"{dia_ini}.{mes_ini}.{ano_ini}"
        session.findById("wnd[0]/usr/ctxtSO_BUDAT-HIGH").text = f"{dia_fim}.{mes_fim}.{ano_fim}"

        session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "/P&L"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except:
            pass

        caminho_arquivo = meta_arquivos['engdds_zfi_gl_pivb.py']['path']
        nome_base = meta_arquivos['engdds_zfi_gl_pivb.py']['files']
        nome_arquivo = f"{ano_ini}_{mes_ini}_{nome_base}"

        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/shellcont/shell").pressToolbarButton("SHOWBUT")
            session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")
            session.findById("wnd[0]/shellcont/shell").selectContextMenuItem("&XXL")

            session.findById("wnd[1]/tbar[0]/btn[0]").press()
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = caminho_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        arquivo = minio.buffer_creator(caminho_arquivo, nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)

        sap.limpar_processos()
        sap.cleanup()

    except Exception as e:
        logging.error(f'Erro ao exportar dados do relatório ZFI_GL_PIVB :: {str(e)}')
        sap.limpar_processos()
        sap.cleanup()

    time.sleep(10)
    minio.flush_pending_uploads()


if __name__ == "__main__":
    engdds_zfi_gl_pivb_main()
