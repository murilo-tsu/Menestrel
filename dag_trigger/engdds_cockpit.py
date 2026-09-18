from saplogin import SAPLogin
from Minio import MinioConnector
import datetime
import json
import time
import os
import logging
sap = SAPLogin()


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


def engdds_cockpit_main():
    logging.info("---- INICIANDO PROCESSO: ENGDDS_COCKPIT.PY ----")

    # 2025-11-18: Instanciando o Minio para utilizar buffer e uploader a partir dos arquivos do json
    minio = MinioConnector()
    erros = []
    with open('files.json','rb') as file:
        meta_arquivos = json.load(file)

    def extrair_zpp_cockpit():
        session = sap.login_to_s4hana()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZPP_COCKPIT"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/btn%_S_ZSTEP_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "3"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "5"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").text = "6"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]").text = "7"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]").text = "8"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        # Limitando a seleção do cockpit
        session.findById("wnd[0]/usr/btn%_S_WERKS_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "E60*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "P60*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").text = "E89*"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/shellcont/shell").selectColumn ("ZSTEP")
        session.findById("wnd[0]/shellcont/shell").contextMenu()
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
            session.findById("wnd[1]").sendVKey (4)
            # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
            # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
            # session.findById("wnd[2]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Cockpit"
            session.findById("wnd[2]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_cockpit.py']['path']
            # session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "ZPP_COCKPIT.XLSX"
            nome_arquivo = meta_arquivos['engdds_cockpit.py']['files'][0]
            session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = nome_arquivo
            # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
            session.findById("wnd[2]/tbar[0]/btn[11]").press()
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        sap.limpar_processos()
        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # sap.upload_files(f"Shared Documents/Hadoop/SAP4HANA/Cockpit/",
        #                  f"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/Cockpit/ZPP_COCKPIT.XLSX")
        arquivo = minio.buffer_creator(meta_arquivos['engdds_cockpit.py']['path'], nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        sap.cleanup()

    executar_com_retry(erros=erros, etapa="ZPP_COCKPIT", funcao=extrair_zpp_cockpit, tentativas=3, intervalo=60)

    minio.flush_pending_uploads()

    if erros:
        raise RuntimeError(
            "Ocorreram erros em uma ou mais extrações de COCKPIT:\n"
            + "\n".join(erros)
        )

    logging.info("---- ENGDDS_COCKPIT.PY finalizado com sucesso ----")

if __name__ == "__main__":
    engdds_cockpit_main()
