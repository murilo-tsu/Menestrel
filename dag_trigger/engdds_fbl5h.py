from datetime import date, timedelta
import json
import time
import os
import logging

from saplogin import SAPLogin
from Minio import MinioConnector


def datas_para_processar():
    """
    Define automaticamente quais datas serão extraídas.

    Regras:
        - Segunda a sexta: baixa somente D0 (dia atual).
        - Sábado e domingo: reconstrói a semana atual (S0) e a anterior (S-1).
    """
    hoje = date.today()
    final_de_semana = hoje.weekday() in (5, 6)  # 5 = sábado | 6 = domingo

    datas = []

    if final_de_semana:
        inicio_semana_atual = hoje - timedelta(days=hoje.weekday())
        inicio_semana_anterior = inicio_semana_atual - timedelta(days=7)

        data_loop = inicio_semana_anterior
        while data_loop <= hoje:
            datas.append(data_loop)
            data_loop += timedelta(days=1)
    else:
        datas.append(hoje)

    return sorted(list(set(datas)))


def data_sap(data_ref):
    """Converte a data de referência para o formato esperado pelo SAP (dd.mm.yyyy)."""
    return data_ref.strftime("%d.%m.%Y")


def nome_arquivo_fbl5h(data_ref):
    """Monta o nome do arquivo de saída com a data da extração."""
    return f"FBL5H_{data_ref:%Y%m%d}.XLSX"


def limpar_arquivos_antigos(minio, bucket, datas_validas):
    """Remove do MinIO arquivos FBL5H fora da janela S0/S-1 atual."""
    objetos = minio.list_files(bucket)
    if not objetos:
        return

    arquivos_validos = {
        nome_arquivo_fbl5h(data_ref)
        for data_ref in datas_validas
    }

    for nome_objeto in objetos:
        if not nome_objeto.startswith("FBL5H_"):
            continue

        if nome_objeto not in arquivos_validos:
            logging.info(f"Removendo arquivo antigo :: {nome_objeto}")
            minio.delete_file(bucket, nome_objeto)


sap = SAPLogin()


def engdds_fbl5h_main():
    logging.info("---- INICIANDO PROCESSO: ENGDDS_FBL5H.PY ----")

    minio = MinioConnector()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, "files.json")

    with open(files_json_path, "r", encoding="utf-8") as file:
        meta_arquivos = json.load(file)

    pasta_destino = meta_arquivos["engdds_fbl5h.py"]["path"]

    datas = datas_para_processar()
    erros = []
    final_de_semana = date.today().weekday() in (5, 6)

    for data_ref in datas:
        data_formatada = data_sap(data_ref)
        nome_arquivo = nome_arquivo_fbl5h(data_ref)

        logging.info(f"Iniciando extração FBL5H para {data_formatada} => {nome_arquivo}")

        try:
            session = sap.login_to_s4hana()

            try:
                session.FindById("wnd[0]").SendVKey(0)
            except:
                pass

            session.findById("wnd[0]/tbar[0]/okcd").text = "FBL5H"
            session.findById("wnd[0]").sendVKey(0)

            session.findById("wnd[0]/usr/ctxtS_CCODE-LOW").text = "E900"
            session.findById("wnd[0]/usr/ctxtP_KEYDO").text = data_formatada
            session.findById("wnd[0]/usr/ctxtP_LAYOUT").text = "/AR FI"
            session.findById("wnd[0]/usr/ctxtP_LAYOUT").setFocus()
            session.findById("wnd[0]/usr/ctxtP_LAYOUT").caretPosition = 6
            session.findById("wnd[0]/tbar[1]/btn[8]").press()

            session.findById("wnd[0]/shellcont/shell").setCurrentCell(-1, "BLART")
            session.findById("wnd[0]/shellcont/shell").selectColumn("BLART")
            session.findById("wnd[0]/shellcont/shell").pressToolbarButton("&MB_FILTER")
            session.findById(
                "wnd[1]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW"
            ).text = "RV"
            session.findById(
                "wnd[1]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW"
            ).caretPosition = 2
            session.findById("wnd[1]/tbar[0]/btn[0]").press()

            sap.kill_excel()
            with sap.export_watchdog(180):
                session.findById("wnd[0]/shellcont/shell").pressToolbarButton("SHOWBUT")
                session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")
                session.findById("wnd[0]/shellcont/shell").selectContextMenuItem("&XXL")
                session.findById("wnd[1]/tbar[0]/btn[0]").press()

                session.findById("wnd[1]/usr/ctxtDY_PATH").text = pasta_destino
                session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
                session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = len(nome_arquivo)
                session.findById("wnd[1]/tbar[0]/btn[0]").press()

            arquivo = minio.buffer_creator(pasta_destino, nome_arquivo)
            minio.upload_or_queue(arquivo, "tmp", nome_arquivo)

            logging.info(f"FBL5H gravado no bucket tmp como {nome_arquivo}")

        except Exception as erro:
            erros.append(f"{data_formatada} -> {str(erro)}")
            logging.error(f"Erro ao processar FBL5H para {data_formatada}: {str(erro)}")

        finally:
            try:
                sap.limpar_processos()
                sap.cleanup()
            except:
                pass

            time.sleep(10)

    minio.flush_pending_uploads()

    if final_de_semana:
        try:
            limpar_arquivos_antigos(minio, "tmp", datas)
            logging.info("Limpeza de arquivos antigos concluída.")
        except Exception as erro_limpeza:
            logging.error(f"Erro ao limpar arquivos antigos: {str(erro_limpeza)}")

    if erros:
        raise RuntimeError(f"Ocorreram erros na extração FBL5H: {erros}")


if __name__ == "__main__":
    engdds_fbl5h_main()
