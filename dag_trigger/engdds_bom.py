# Create an instance of the SAPLogin class
from dateutil.relativedelta import relativedelta
from saplogin import SAPLogin
from Minio import MinioConnector
import datetime
import json
import time
import os
import logging
sap = SAPLogin()

def f(num):
    """Função f() normaliza os números em formato texto"""
    return f"0{num}" if num < 10 else str(num)


def registrar_erro(erros, etapa, erro):
    """
    Registra erro definitivo de uma etapa.

    Essa função só deve ser chamada depois que todas as tentativas da etapa
    falharem.
    """
    mensagem = f"{etapa} :: {str(erro)}"

    logging.error(f"Erro definitivo na etapa {etapa}: {str(erro)}", exc_info=erro)
    erros.append(mensagem)

    try:
        sap.limpar_processos()
        sap.cleanup()
    except Exception as erro_cleanup:
        logging.debug(f"Falha ao limpar processos após erro definitivo em {etapa}: {erro_cleanup}")


def executar_com_retry(erros, etapa, funcao, tentativas=3, intervalo=60):
    """
    Executa uma etapa com tentativas.

    Regra:
        - Se a etapa funcionar em qualquer tentativa, segue o fluxo normalmente.
        - Se falhar, encerra o SAP, aguarda e tenta novamente.
        - Se todas as tentativas falharem, registra o erro na lista 'erros'.
        - O script não para imediatamente, permitindo executar os próximos blocos.
    """
    ultimo_erro = None

    for tentativa in range(1, tentativas + 1):
        try:
            logging.info(f"{etapa} :: tentativa {tentativa}/{tentativas}")

            funcao()

            logging.info(f"{etapa} :: concluído com sucesso")
            return True

        except Exception as erro:
            ultimo_erro = erro

            logging.error(
                f"Erro na etapa {etapa} durante tentativa "
                f"{tentativa}/{tentativas}: {str(erro)}",
                exc_info=erro
            )

            try:
                sap.limpar_processos()
                sap.cleanup()
            except Exception as erro_cleanup:
                logging.debug(f"Falha ao limpar processos após tentativa de {etapa}: {erro_cleanup}")

            if tentativa < tentativas:
                logging.info(f"{etapa} será tentado novamente em {intervalo} segundos...")
                time.sleep(intervalo)

    registrar_erro(erros, etapa, ultimo_erro)
    return False


def engdds_bom_main():
    logging.info("---- INICIANDO PROCESSO: ENGDDS_BOM.PY ----")

    # 2025-11-18: Instanciando o Minio para utilizar buffer e uploader a partir dos arquivos do json
    minio = MinioConnector()
    erros = []
    with open('files.json','rb') as file:
        meta_arquivos = json.load(file)

    end_year_bom = f(datetime.date.today().year)
    end_month_bom = f(datetime.date.today().month)
    end_day_bom = f(datetime.date.today().day)

    first_date = datetime.datetime(datetime.date.today().year, datetime.date.today().month, 1)
    last_date = first_date + relativedelta(months=+12)
    first_date = first_date.strftime("%d.%m.%Y")
    last_date = last_date.strftime("%d.%m.%Y")

    # E890 :: COMPLEXO MINEROINDUSTRIAL DE SERRA DO SALITRE
    def extrair_bomrep_e890():
        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZPP_BOMREP"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtS_WERKS-LOW").text = "E89*"
        session.findById("wnd[0]/usr/ctxtS_STLAN-LOW").text = "1"
        session.findById("wnd[0]/usr/ctxtS_DATUV-LOW").text = first_date
        session.findById("wnd[0]/usr/ctxtS_VAL_TO-LOW").text = last_date

        # 2025-12-09: Criando um layout público para o DATAINSIGHTS
        # session.findById("wnd[0]/usr/ctxtP_VARI").text = "DATAINSIGHTS"
        session.findById("wnd[0]/usr/ctxtP_VARI").text = "/DATAINSIGHT"
        session.findById("wnd[0]/usr/txtS_STLAL-LOW").setFocus()
        session.findById("wnd[0]/usr/txtS_STLAL-LOW").caretPosition = 0
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()

        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\BOM"
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_bom.py']['path']
        nome_arquivo = f"{end_year_bom}-{end_month_bom}-{end_day_bom} {meta_arquivos['engdds_bom.py']['files'][0]}"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 8
        session.findById("wnd[1]").sendVKey (0)
        logging.info(f"ATUALIZADO: {meta_arquivos['engdds_bom.py']['path']}/{nome_arquivo}")

        # Encerrar sessão do SAP
        sap.limpar_processos()
        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # sap.upload_files(f"Shared Documents/Hadoop/SAP4HANA/BOM/",
        #                  f"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/BOM/{end_year_bom}-{end_month_bom}-{end_day_bom} ZPP_BOMREP_E890.XLSX")
        arquivo = minio.buffer_creator(meta_arquivos['engdds_bom.py']['path'], nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        sap.cleanup()

    # E600 :: PART 1 :: EUROCHEM FERTILIZANTES TOCANTINS
    def extrair_bomrep_e600_pt1():
        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZPP_BOMREP"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtS_WERKS-LOW").text = "E60A"
        session.findById("wnd[0]/usr/ctxtS_WERKS-HIGH").text = "E60E"
        session.findById("wnd[0]/usr/ctxtS_STLAN-LOW").text = "1"
        session.findById("wnd[0]/usr/ctxtS_DATUV-LOW").text = first_date
        session.findById("wnd[0]/usr/ctxtS_VAL_TO-LOW").text = last_date

        # 2025-12-09: Criando um layout público para o DATAINSIGHTS
        # session.findById("wnd[0]/usr/ctxtP_VARI").text = "DATAINSIGHTS"
        session.findById("wnd[0]/usr/ctxtP_VARI").text = "/DATAINSIGHT"
        session.findById("wnd[0]/usr/txtS_STLAL-LOW").setFocus()
        session.findById("wnd[0]/usr/txtS_STLAL-LOW").caretPosition = 0
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()

        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\BOM"
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_bom.py']['path']
        nome_arquivo = f"{end_year_bom}-{end_month_bom}-{end_day_bom} {meta_arquivos['engdds_bom.py']['files'][1]}"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 8
        session.findById("wnd[1]").sendVKey (0)
        logging.info(f"ATUALIZADO: {meta_arquivos['engdds_bom.py']['path']}/{nome_arquivo}")

        # Encerrar sessão do SAP
        sap.limpar_processos()
        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # sap.upload_files(f"Shared Documents/Hadoop/SAP4HANA/BOM/",
        #                  f"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/BOM/{end_year_bom}-{end_month_bom}-{end_day_bom} ZPP_BOMREP_E600.XLSX")
        arquivo = minio.buffer_creator(meta_arquivos['engdds_bom.py']['path'], nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        sap.cleanup()

    # E600 :: PART 2 :: EUROCHEM FERTILIZANTES TOCANTINS
    def extrair_bomrep_e600_pt2():
        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZPP_BOMREP"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtS_WERKS-LOW").text = "E60F"
        session.findById("wnd[0]/usr/ctxtS_WERKS-HIGH").text = "E60Z"
        session.findById("wnd[0]/usr/ctxtS_STLAN-LOW").text = "1"
        session.findById("wnd[0]/usr/ctxtS_DATUV-LOW").text = first_date
        session.findById("wnd[0]/usr/ctxtS_VAL_TO-LOW").text = last_date

        # 2025-12-09: Criando um layout público para o DATAINSIGHTS
        # session.findById("wnd[0]/usr/ctxtP_VARI").text = "DATAINSIGHTS"
        session.findById("wnd[0]/usr/ctxtP_VARI").text = "/DATAINSIGHT"
        session.findById("wnd[0]/usr/txtS_STLAL-LOW").setFocus()
        session.findById("wnd[0]/usr/txtS_STLAL-LOW").caretPosition = 0
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()

        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\BOM"
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_bom.py']['path']
        nome_arquivo = f"{end_year_bom}-{end_month_bom}-{end_day_bom} {meta_arquivos['engdds_bom.py']['files'][2]}"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 8
        session.findById("wnd[1]").sendVKey (0)
        logging.info(f"ATUALIZADO: {meta_arquivos['engdds_bom.py']['path']}/{nome_arquivo}")

        # Encerrar sessão do SAP
        sap.limpar_processos()
        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # sap.upload_files(f"Shared Documents/Hadoop/SAP4HANA/BOM/",
        #                  f"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/BOM/{end_year_bom}-{end_month_bom}-{end_day_bom} ZPP_BOMREP_E600.XLSX")
        arquivo = minio.buffer_creator(meta_arquivos['engdds_bom.py']['path'], nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        sap.cleanup()

    # E900 :: EUROCHEM FERTILIZANTES HERINGER
    def extrair_bomrep_e900():
        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZPP_BOMREP"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtS_WERKS-LOW").text = "E90*"
        session.findById("wnd[0]/usr/ctxtS_STLAN-LOW").text = "1"
        session.findById("wnd[0]/usr/ctxtS_DATUV-LOW").text = first_date
        session.findById("wnd[0]/usr/ctxtS_VAL_TO-LOW").text = last_date

        # 2025-12-09: Criando um layout público para o DATAINSIGHTS
        # session.findById("wnd[0]/usr/ctxtP_VARI").text = "DATAINSIGHTS"
        session.findById("wnd[0]/usr/ctxtP_VARI").text = "/DATAINSIGHT"
        session.findById("wnd[0]/usr/txtS_STLAL-LOW").setFocus()
        session.findById("wnd[0]/usr/txtS_STLAL-LOW").caretPosition = 0
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()

        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\BOM"
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_bom.py']['path']
        # session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = f"{end_year_bom}-{end_month_bom}-{end_day_bom} ZPP_BOMREP_E900.XLSX"
        nome_arquivo = f"{end_year_bom}-{end_month_bom}-{end_day_bom} {meta_arquivos['engdds_bom.py']['files'][3]}"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 8
        session.findById("wnd[1]").sendVKey (0)
        logging.info(f"ATUALIZADO: {meta_arquivos['engdds_bom.py']['path']}/{nome_arquivo}")

        # Encerrar sessão do SAP
        sap.limpar_processos()
        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # sap.upload_files(f"Shared Documents/Hadoop/SAP4HANA/BOM/",
        #                  f"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/BOM/{end_year_bom}-{end_month_bom}-{end_day_bom} ZPP_BOMREP_E900.XLSX")
        arquivo = minio.buffer_creator(meta_arquivos['engdds_bom.py']['path'], nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------------
        sap.cleanup()

    executar_com_retry(erros=erros, etapa="ZPP_BOMREP_E890", funcao=extrair_bomrep_e890, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="ZPP_BOMREP_E600_PT1", funcao=extrair_bomrep_e600_pt1, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="ZPP_BOMREP_E600_PT2", funcao=extrair_bomrep_e600_pt2, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="ZPP_BOMREP_E900", funcao=extrair_bomrep_e900, tentativas=3, intervalo=60)

    time.sleep(10)
    minio.flush_pending_uploads()

    if erros:
        raise RuntimeError(
            "Ocorreram erros em uma ou mais extrações de BOM:\n"
            + "\n".join(erros)
        )

    logging.info("---- ENGDDS_BOM.PY finalizado com sucesso ----")


if __name__ == "__main__":
    engdds_bom_main()
