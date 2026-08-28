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

    Regra:
        - Segunda a sexta: processa apenas D-1.
        - Sábado e domingo: processa os últimos 10 dias fechados, de D-10 até D-1.

    Observação:
        O dia atual nunca é processado, pois a FBL3H trabalha com dados fechados.
    """
    hoje = date.today()
    final_de_semana = hoje.weekday() in (5, 6)  # 5 = sábado | 6 = domingo

    qtd_dias = 10 if final_de_semana else 1

    data_final = hoje - timedelta(days=1)
    data_inicial = data_final - timedelta(days=qtd_dias - 1)

    return [
        data_inicial + timedelta(days=i)
        for i in range(qtd_dias)
    ]


def data_sap(data_ref):
    """Converte a data de referência para o formato esperado pelo SAP (dd.mm.yyyy)."""
    return data_ref.strftime("%d.%m.%Y")


def nome_arquivo_fbl3h(data_ref):
    """Monta o nome do arquivo de saída com a data da extração."""
    return f"FBL3H_{data_ref:%Y%m%d}.XLSX"


# Instanciador de SAP Session
sap = SAPLogin()


def engdds_fbl3h_main():
    """
    Executa a extração da transação FBL3H no SAP S/4HANA.

    Fluxo:
        1. Identifica as datas a serem processadas.
        2. Para cada data, acessa a transação FBL3H.
        3. Exporta o relatório em Excel para a pasta TEMP da VM.
        4. Envia o arquivo gerado para o bucket tmp do MinIO.
    """
    logging.info("---- INICIANDO PROCESSO: ENGDDS_FBL3H.PY ----")

    minio = MinioConnector()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, "files.json")

    with open(files_json_path, "r", encoding="utf-8") as file:
        meta_arquivos = json.load(file)

    pasta_destino = meta_arquivos["engdds_fbl3h.py"]["path"]

    datas = datas_para_processar()
    erros = []

    for data_ref in datas:
        data_formatada = data_sap(data_ref)
        nome_arquivo = nome_arquivo_fbl3h(data_ref)

        logging.info(f"Iniciando extração FBL3H para {data_formatada} => {nome_arquivo}")

        try:
            session = sap.login_to_s4hana()

            try:
                session.FindById("wnd[0]").SendVKey(0)
            except:
                pass

            session.findById("wnd[0]/tbar[0]/okcd").text = "FBL3H"
            session.findById("wnd[0]").sendVKey(0)

            session.findById("wnd[0]/usr/ctxtS_CCODE-LOW").text = "E900"
            session.findById("wnd[0]/usr/ctxtS_CCODE-HIGH").text = "E900"

            session.findById("wnd[0]/usr/radP_AI").setFocus()
            session.findById("wnd[0]/usr/radP_AI").select()

            session.findById("wnd[0]/usr/ctxtS_PDATE-LOW").text = data_formatada
            session.findById("wnd[0]/usr/ctxtS_PDATE-HIGH").text = data_formatada

            session.findById("wnd[0]/usr/ctxtP_LAYOUT").text = "/FPA_HRG"
            session.findById("wnd[0]/tbar[1]/btn[8]").press()

            try:
                session.findById("wnd[1]/usr/btnBUTTON_1").press()
            except:
                pass

            sap.kill_excel()
            with sap.export_watchdog(180):
                session.findById("wnd[0]/shellcont/shell").pressToolbarButton("SHOWBUT")
                session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")
                session.findById("wnd[0]/shellcont/shell").selectContextMenuItem("&XXL")

                session.findById("wnd[1]/tbar[0]/btn[0]").press()
                session.findById("wnd[1]/tbar[0]/btn[0]").press()

                session.findById("wnd[1]/usr/ctxtDY_PATH").text = pasta_destino
                session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
                session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = len(nome_arquivo)

                session.findById("wnd[1]/tbar[0]/btn[0]").press()

            arquivo = minio.buffer_creator(pasta_destino, nome_arquivo)
            minio.upload_or_queue(arquivo, "tmp", nome_arquivo)

            logging.info(f"{data_formatada} :: FBL3H gravado no tmp como {nome_arquivo}")

        except Exception as erro:
            logging.error(f"Erro ao processar FBL3H para {data_formatada}: {str(erro)}")
            erros.append((data_formatada, str(erro)))

        finally:
            try:
                sap.limpar_processos()
                sap.cleanup()
            except:
                pass

            time.sleep(10)

    minio.flush_pending_uploads()

    if erros:
        raise RuntimeError(f"Ocorreram erros na extração FBL3H: {erros}")


if __name__ == "__main__":
    engdds_fbl3h_main()
