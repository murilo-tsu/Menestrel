from saplogin import SAPLogin
from Minio import MinioConnector
import datetime
import json
import time
import os
import logging
sap = SAPLogin()

def remover_arquivo_local(caminho_arquivo):
    """
    Remove o arquivo local antes de uma nova exportação.

    Isso evita que o SAP tente sobrescrever um XLSX antigo ou que o Python leia
    um arquivo antigo que ficou na pasta de saída.
    """
    if not os.path.exists(caminho_arquivo):
        return

    logging.info(f"Arquivo local já existe e será removido: {caminho_arquivo}")

    try:
        os.remove(caminho_arquivo)
    except PermissionError as erro:
        raise PermissionError(
            f"Não foi possível remover o arquivo local porque ele está em uso: "
            f"{caminho_arquivo}. Verifique se ele está aberto no Excel ou preso "
            f"por algum processo do SAP."
        ) from erro


def aguardar_arquivo_disponivel(caminho_arquivo, tentativas=20, intervalo=3):
    """
    Aguarda o arquivo existir e estar liberado para leitura.

    Mesmo após o SAP informar que exportou, o arquivo XLSX pode continuar sendo
    gravado ou ficar temporariamente bloqueado pelo Excel/SAP.
    """
    for tentativa in range(1, tentativas + 1):
        if not os.path.exists(caminho_arquivo):
            logging.info(
                f"Arquivo ainda não encontrado. "
                f"Tentativa {tentativa}/{tentativas}: {caminho_arquivo}"
            )
            time.sleep(intervalo)
            continue

        try:
            with open(caminho_arquivo, "rb") as file:
                file.read(1)
            return

        except PermissionError:
            logging.info(
                f"Arquivo ainda está bloqueado. "
                f"Tentativa {tentativa}/{tentativas}. "
                f"Aguardando {intervalo} segundos..."
            )
            time.sleep(intervalo)

    raise TimeoutError(
        f"O arquivo foi exportado, mas continuou bloqueado para leitura após "
        f"{tentativas * intervalo} segundos: {caminho_arquivo}"
    )

def engdds_faturamento_hourly_main():
    logging.info("---- INICIANDO PROCESSO: ENGDDS_FATURAMENTO_HOURLY.PY ----")

    minio = MinioConnector()
    with open('files.json', 'rb') as file:
        meta_arquivos = json.load(file)

    # Definindo datas dinâminas
    now = time.localtime()
    start_date = datetime.datetime(now.tm_year,now.tm_mon,now.tm_mday) + datetime.timedelta(days=-2)
    #start_date = datetime.datetime(2025,1,1)
    start_day = start_date.day
    start_month = start_date.month
    start_year = start_date.year
    end_day = now.tm_mday
    end_month = now.tm_mon
    end_year = now.tm_year

    try:
        # Login to S/4HANA
        session = sap.login_to_s4hana()
        # Extrair E600

        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZSD_PIVB"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "/DATAINSIGHT"
        session.findById("wnd[0]/usr/ctxtSO_VKORG-LOW").text = "E600"
        session.findById("wnd[0]/usr/ctxtFB_FKDAT-LOW").text = f"{start_day}.{start_month}.{start_year}"
        session.findById("wnd[0]/usr/ctxtFB_FKDAT-HIGH").text = f"{end_day}.{end_month}.{end_year}"
        session.findById("wnd[0]/usr/ctxtP_DISVAR").caretPosition = 4
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except:
            pass

        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("TECHNAM")
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")

            # Opção 2: usado para extrair um arquivo do tipo .xlsx
            session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_faturamento_hourly.py']['path']
            nome_arquivo = meta_arquivos['engdds_faturamento_hourly.py']['files'][0]
            caminho_arquivo_local = os.path.join(meta_arquivos['engdds_faturamento_hourly.py']['path'], nome_arquivo)
            remover_arquivo_local(caminho_arquivo_local)
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 18
            session.findById("wnd[1]/tbar[0]/btn[11]").press()
        session.findById("wnd[0]").close()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        aguardar_arquivo_disponivel(caminho_arquivo_local)
        arquivo = minio.buffer_creator(meta_arquivos['engdds_faturamento_hourly.py']['path'], nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        sap.cleanup()

    finally:
        sap.limpar_processos()
        sap.cleanup()

    try:

        session = sap.login_to_s4hana()
        # Extrair E890
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZSD_PIVB"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "/DATAINSIGHT"
        session.findById("wnd[0]/usr/ctxtSO_VKORG-LOW").text = "E890"
        session.findById("wnd[0]/usr/ctxtFB_FKDAT-LOW").text = f"{start_day}.{start_month}.{start_year}"
        session.findById("wnd[0]/usr/ctxtFB_FKDAT-HIGH").text = f"{end_day}.{end_month}.{end_year}"
        session.findById("wnd[0]/usr/ctxtP_DISVAR").caretPosition = 4
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except:
            pass

        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("TECHNAM")
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")

            # Opção 2: usado para extrair um arquivo do tipo .xlsx
            session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_faturamento_hourly.py']['path']
            nome_arquivo = meta_arquivos['engdds_faturamento_hourly.py']['files'][1]
            caminho_arquivo_local = os.path.join(meta_arquivos['engdds_faturamento_hourly.py']['path'], nome_arquivo)
            remover_arquivo_local(caminho_arquivo_local)
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 18
            session.findById("wnd[1]/tbar[0]/btn[11]").press()
        session.findById("wnd[0]").close()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        aguardar_arquivo_disponivel(caminho_arquivo_local)
        arquivo = minio.buffer_creator(meta_arquivos['engdds_faturamento_hourly.py']['path'], nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        sap.cleanup()

    finally:
        sap.limpar_processos()
        sap.cleanup()


    try:

        session = sap.login_to_s4hana()
        # Extrair E900
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZSD_PIVB"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "/DATAINSIGHT"
        session.findById("wnd[0]/usr/ctxtSO_VKORG-LOW").text = "E900"
        session.findById("wnd[0]/usr/ctxtFB_FKDAT-LOW").text = f"{start_day}.{start_month}.{start_year}"
        session.findById("wnd[0]/usr/ctxtFB_FKDAT-HIGH").text = f"{end_day}.{end_month}.{end_year}"
        session.findById("wnd[0]/usr/ctxtP_DISVAR").caretPosition = 4
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except:
            pass

        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("TECHNAM")
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")

            # Opção 2: usado para extrair um arquivo do tipo .xlsx
            session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_faturamento_hourly.py']['path']
            nome_arquivo = meta_arquivos['engdds_faturamento_hourly.py']['files'][2]
            caminho_arquivo_local = os.path.join(meta_arquivos['engdds_faturamento_hourly.py']['path'], nome_arquivo)
            remover_arquivo_local(caminho_arquivo_local)
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 18
            session.findById("wnd[1]/tbar[0]/btn[11]").press()
        session.findById("wnd[0]").close()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        aguardar_arquivo_disponivel(caminho_arquivo_local)
        arquivo = minio.buffer_creator(meta_arquivos['engdds_faturamento_hourly.py']['path'], nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        sap.cleanup()

    except Exception as e:
        logging.error(f'Erro ao exportar dados do relatório ZSD_PIVB :: {str(e)}')
        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.cleanup()

    time.sleep(5)
    minio.flush_pending_uploads()
    # Os fluxos deixaram de triggar as dags
    #sap.trigger_airflow_dag(dag_name="engdds_faturamento")

if __name__ == "__main__":
    engdds_faturamento_hourly_main()
