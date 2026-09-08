from saplogin import SAPLogin
from datetime import date
from Minio import MinioConnector
import pandas as pd
import json
import time
import os
import logging

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

    logging.error(f"Erro definitivo na etapa {etapa}: {str(erro)}")
    erros.append(mensagem)

    try:
        sap.limpar_processos()
        sap.cleanup()
    except:
        pass


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
                f"{tentativa}/{tentativas}: {str(erro)}"
            )

            try:
                sap.limpar_processos()
                sap.cleanup()
            except:
                pass

            if tentativa < tentativas:
                logging.info(f"{etapa} será tentado novamente em {intervalo} segundos...")
                time.sleep(intervalo)

    registrar_erro(erros, etapa, ultimo_erro)
    return False


# Instaciador de SAP Session
sap = SAPLogin()

def engdds_estoque_main():
    """
    Executa as extrações de estoque no SAP S/4HANA.

    Fluxo:
        1. Carrega os metadados do files.json.
        2. Extrai o relatório ZMM_QNTY_PIVB por data e por planta.
        3. Extrai o relatório ZMB5T.
        4. Extrai a tabela MCHB via SE16N.
        5. Envia os arquivos gerados para o bucket tmp do MinIO.

    Observação:
        Cada extração possui retry próprio. Para o ZMM_QNTY_PIVB,
        o retry é feito por data + planta, evitando repetir tudo se
        apenas uma combinação falhar.
    """
    logging.info("---- INICIANDO PROCESSO: ENGDDS_ESTOQUE.PY ----")

    minio = MinioConnector()
    erros = []

    with open('files.json', 'rb') as file:
        meta_arquivos = json.load(file)

    path_estoque = meta_arquivos["engdds_estoque.py"]["path"][0]
    path_mchb = meta_arquivos["engdds_estoque.py"]["path"][1]
    files = meta_arquivos["engdds_estoque.py"]["files"]
    sufixo_files = meta_arquivos["engdds_estoque.py"]["sufixo_files"]
    bukrs = meta_arquivos["engdds_estoque.py"]["bukrs"]

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO 1 :: EXTRAÇÃO ZMM_QNTY_PIVB
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def extrair_zmm_qnty_pivb_data_bukrs(dt, bukrs_code):
        """
        Executa uma extração do ZMM_QNTY_PIVB para uma data e uma empresa (BUKRS).

        Essa função é chamada pelo retry individual de cada combinação:
            data + empresa
        """
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZMM_QNTY_PIVB"
        session.findById("wnd[0]").sendVKey(0)

        session.findById("wnd[0]/usr/ctxtSO_BUKRS-LOW").text = f"{bukrs_code}"
        session.findById("wnd[0]/usr/ctxtSO_BUDAT-LOW").text = (
            f"01.{f(dt.month)}.{dt.year}"
        )
        session.findById("wnd[0]/usr/ctxtSO_BUDAT-HIGH").text = (
            f"{f(dt.day)}.{f(dt.month)}.{dt.year}"
        )

        session.findById(
            "wnd[0]/usr/btn%_SO_MATNR_%_APP_%-VALU_PUSH"
        ).press()

        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpINTL").select()

        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpINTL/"
            "ssubSCREEN_HEADER:SAPLALDB:3020/"
            "tblSAPLALDBINTERVAL/ctxtRSCSEL_255-ILOW_I[1,0]"
        ).text = "1000000000"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpINTL/"
            "ssubSCREEN_HEADER:SAPLALDB:3020/"
            "tblSAPLALDBINTERVAL/ctxtRSCSEL_255-IHIGH_I[2,0]"
        ).text = "1999999999"

        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpINTL/"
            "ssubSCREEN_HEADER:SAPLALDB:3020/"
            "tblSAPLALDBINTERVAL/ctxtRSCSEL_255-ILOW_I[1,1]"
        ).text = "2000000000"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpINTL/"
            "ssubSCREEN_HEADER:SAPLALDB:3020/"
            "tblSAPLALDBINTERVAL/ctxtRSCSEL_255-IHIGH_I[2,1]"
        ).text = "2999999999"

        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpINTL/"
            "ssubSCREEN_HEADER:SAPLALDB:3020/"
            "tblSAPLALDBINTERVAL/ctxtRSCSEL_255-ILOW_I[1,2]"
        ).text = "4000000000"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpINTL/"
            "ssubSCREEN_HEADER:SAPLALDB:3020/"
            "tblSAPLALDBINTERVAL/ctxtRSCSEL_255-IHIGH_I[2,2]"
        ).text = "4999999999"

        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpINTL/"
            "ssubSCREEN_HEADER:SAPLALDB:3020/"
            "tblSAPLALDBINTERVAL/ctxtRSCSEL_255-ILOW_I[1,3]"
        ).text = "7000000000"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpINTL/"
            "ssubSCREEN_HEADER:SAPLALDB:3020/"
            "tblSAPLALDBINTERVAL/ctxtRSCSEL_255-IHIGH_I[2,3]"
        ).text = "7999999999"

        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "/IT_INV_EXT"
        session.findById("wnd[0]/usr/ctxtP_DISVAR").setFocus()
        session.findById("wnd[0]/usr/ctxtP_DISVAR").caretPosition = 4
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except:
            pass

        session.findById("wnd[0]/shellcont/shell").pressToolbarButton("SHOWBUT")
        session.findById("wnd[0]/shellcont/shell").pressToolbarButton("TECHNAM")

        nome_arquivo = (
            f"{dt.year}-{f(dt.month)}-{f(dt.day)} "
            f"{files[3]}"
            f"{bukrs_code}"
            f"{sufixo_files}"
        )

        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")
            session.findById("wnd[0]/shellcont/shell").selectContextMenuItem("&XXL")

            try:
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except:
                pass

            session.findById("wnd[1]/usr/ctxtDY_PATH").text = path_estoque
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        arquivo = minio.buffer_creator(path_estoque, nome_arquivo)
        minio.upload_or_queue(arquivo, "tmp", nome_arquivo)

        # Encerrar sessão do SAP após cada planta
        sap.limpar_processos()
        sap.cleanup()

    def bloco_zmm_qnty_pivb():
        """
        Executa a janela de extração do ZMM_QNTY_PIVB.

        O retry é aplicado por data + empresa (BUKRS), e não no bloco inteiro.
        Assim, se uma empresa falhar, o script tenta novamente só aquela empresa
        e depois segue para as próximas combinações.
        """
        # Artifício <--> usar dt_comp para tirar fotos de estoque em outras datas
        # SE necessário; por enquanto inativo, extrai só a data de hoje.
        primeira_data = date.today()

        dates_range = pd.date_range(primeira_data, pd.Timestamp.now(), freq="D")
        dt_comp = [date.strftime("%Y-%m-%d") for date in dates_range]

        for day in dt_comp:
            dt = date(
                int(day.split("-")[0]),
                int(day.split("-")[1]),
                int(day.split("-")[2]),
            )

            for bukrs_code in bukrs:
                etapa = f"ZMM_QNTY_PIVB {dt.year}-{f(dt.month)}-{f(dt.day)} {bukrs_code}"

                executar_com_retry(
                    erros=erros,
                    etapa=etapa,
                    funcao=lambda dt=dt, bukrs_code=bukrs_code: extrair_zmm_qnty_pivb_data_bukrs(dt, bukrs_code),
                    tentativas=3,
                    intervalo=60,
                )

            logging.info(f"{dt.year}-{f(dt.month)}-{f(dt.day)} :: DADOS PROCESSADOS!")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO 2 :: EXTRAÇÃO ZMB5T
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def bloco_zmb5t():
        now = time.localtime()
        end_day = f(now.tm_mday)
        end_month = f(now.tm_mon)
        end_year = f(now.tm_year)

        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZMB5T"
        session.findById("wnd[0]").sendVKey(0)

        session.findById("wnd[0]/usr/ctxtP_ALVDEF").text = "/Z2"
        session.findById("wnd[0]/usr/ctxtP_ALVDEF").setFocus()
        session.findById("wnd[0]/usr/ctxtP_ALVDEF").caretPosition = 3

        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]").sendVKey(8)

        session.findById("wnd[0]/tbar[1]/btn[43]").press()
        session.findById("wnd[0]/mbar/menu[3]/menu[2]/menu[1]").select()
        session.findById(
            "wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/"
            "cntlD500_CONTAINER/shellcont/shell"
        ).clickCurrentCell()

        nome_arquivo = f"{end_year}-{end_month}-{end_day} {files[1]}"

        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/mbar/menu[0]/menu[1]/menu[1]").select()

            try:
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except:
                pass

            session.findById("wnd[1]/usr/ctxtDY_PATH").text = path_estoque
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 21
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        arquivo = minio.buffer_creator(path_estoque, nome_arquivo)
        minio.upload_or_queue(arquivo, "tmp", nome_arquivo)

        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.cleanup()

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO 3 :: EXTRAÇÃO SE16N / MCHB
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def bloco_mchb():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        now = time.localtime()

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nSE16N"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "MCHB"
        session.findById("wnd[0]").sendVKey(0)

        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").setFocus
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").caretPosition = 0

        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 1
        session.findById(
            "wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/ctxtGS_SELFIELDS-LOW[2,1]"
        ).text = "E90*"

        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 2
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 3
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 4
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 5
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 6
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 7
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 8
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 9

        # Filtro de ano
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").press()
        session.findById("wnd[1]").sendVKey(12)

        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").press()
        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]"
        ).text = f"{now.tm_year}"
        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]"
        ).caretPosition = 4
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        # Filtro de meses
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,2]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,2]").press()

        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]"
        ).text = f"{now.tm_mon}"
        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]"
        ).text = f"{now.tm_mon - 1}"
        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]"
        ).text = f"{now.tm_mon - 2}"
        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,3]"
        ).text = f"{now.tm_mon - 3}"
        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,4]"
        ).text = f"{now.tm_mon - 4}"

        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,4]"
        ).setFocus()
        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,4]"
        ).caretPosition = 1
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        nome_arquivo = files[2]

        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton(
                "&MB_EXPORT"
            )
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem(
                "&XXL"
            )

            try:
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except:
                pass

            session.findById("wnd[1]/usr/ctxtDY_PATH").text = path_mchb
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        arquivo = minio.buffer_creator(path_mchb, nome_arquivo)
        minio.upload_or_queue(arquivo, "tmp", nome_arquivo)

        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.cleanup()

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # EXECUÇÃO DOS BLOCOS COM RETRY
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    bloco_zmm_qnty_pivb()

    executar_com_retry(
        erros=erros,
        etapa="ZMB5T",
        funcao=bloco_zmb5t,
        tentativas=3,
        intervalo=60,
    )

    executar_com_retry(
        erros=erros,
        etapa="SE16N_MCHB",
        funcao=bloco_mchb,
        tentativas=3,
        intervalo=60,
    )

    time.sleep(10)
    minio.flush_pending_uploads()

    if erros:
        raise RuntimeError(
            "Ocorreram erros em uma ou mais extrações de estoque:\n"
            + "\n".join(erros)
        )

    logging.info("---- ENGDDS_ESTOQUE.PY finalizado com sucesso ----")


if __name__ == "__main__":
    engdds_estoque_main()
