# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# IMPORTAR BIBLIOTECAS
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# Bibliotecas :: Gerais
import datetime
import json
import time
import os

# Bibliotecas :: Específicas
from saplogin import SAPLogin
from Minio import MinioConnector


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# INSTANCIANDO VARIÁVEIS DE AMBIENTE :: SAP
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# Instanciador de SAP Session
sap = SAPLogin()


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# FUNÇÕES AUXILIARES
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def f(num):
    """
    Normaliza números menores que 10 para dois dígitos.

    Exemplo:
        1 -> "01"
        10 -> "10"
    """
    return f"0{num}" if num < 10 else str(num)


def registrar_erro(erros, etapa, erro):
    """
    Registra erro definitivo de uma etapa.

    Essa função só deve ser chamada depois que todas as tentativas da etapa
    falharem.
    """
    mensagem = f"{etapa} :: {str(erro)}"

    print(f"Erro definitivo na etapa {etapa}: {str(erro)}")
    erros.append(mensagem)

    try:
        sap.encerrar_sap()
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
            print(
                f" ---------- {etapa} :: tentativa "
                f"{tentativa}/{tentativas} ---------- "
            )

            funcao()

            print(f" ---------- {etapa} :: concluído com sucesso ---------- ")
            return True

        except Exception as erro:
            ultimo_erro = erro

            print(
                f"Erro na etapa {etapa} durante tentativa "
                f"{tentativa}/{tentativas}: {str(erro)}"
            )

            try:
                sap.encerrar_sap()
            except:
                pass

            if tentativa < tentativas:
                print(
                    f"{etapa} será tentado novamente em "
                    f"{intervalo} segundos..."
                )
                time.sleep(intervalo)

    registrar_erro(erros, etapa, ultimo_erro)
    return False


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# INICIANDO PROCESSAMENTO :: EXTRAÇÃO SAP4HANA COMPRAS
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def engdds_compras_main():
    """
    Executa as extrações de compras no SAP S/4HANA.

    Fluxo:
        1. Carrega os metadados do files.json.
        2. Extrai relatório ME2W.
        3. Extrai relatório ME5A.
        4. Extrai tabela EBAN via SE16N.
        5. Extrai tabela EKKO via SE16N.
        6. Extrai tabela EKPO via SE16N.
        7. Extrai relatório ZMM_PURDOCS_REPORT.
        8. Extrai textos de cabeçalho do ZMM_PURDOCS_REPORT.
        9. Extrai informações auxiliares do ZMM_PURDOCS_REPORT.
        10. Envia os arquivos gerados para o bucket tmp do MinIO.

    Observação:
        As etapas são independentes. Se uma falhar, o script tenta executar
        as próximas e só informa falha ao Menestrel no final.

        Cada etapa possui retry próprio. Se uma tentativa falhar, o SAP é
        encerrado, o script aguarda e tenta novamente.
    """
    print(" ---------- Iniciando extração SAP4HANA :: Compras ---------- ")

    minio = MinioConnector()
    erros = []

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # CARREGANDO METADADOS DOS ARQUIVOS
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    print("Carregando metadados do arquivo files.json...")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, "files.json")

    with open(files_json_path, "r", encoding="utf-8") as file:
        meta_arquivos = json.load(file)

    print("Metadados carregados com sucesso.")

    path_compras = meta_arquivos["engdds_compras.py"]["path"][0]
    path_tabelas = meta_arquivos["engdds_compras.py"]["path"][1]
    files = meta_arquivos["engdds_compras.py"]["files"]

    print(f"Path de relatórios de compras: {path_compras}")
    print(f"Path de tabelas de compras: {path_tabelas}")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # DEFININDO DATA PARA NOMES DOS ARQUIVOS
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    end_year_compras = f(datetime.date.today().year)
    end_month_compras = f(datetime.date.today().month)
    end_day_compras = f(datetime.date.today().day)

    data_nome_arquivo = f"{end_year_compras}-{end_month_compras}-{end_day_compras}"

    print(f"Data utilizada nos nomes dos arquivos: {data_nome_arquivo}")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO 1 :: ME2W - PEDIDOS POR PLANTA FORNECEDORA
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def bloco_me2w():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        print("Iniciando extração da ME2W!")

        session.findById("wnd[0]/tbar[0]/okcd").text = "ME2W"
        session.findById("wnd[0]").sendVKey(0)

        # Organização de compras
        session.findById("wnd[0]/usr/btn%_EW_EKORG_%_APP_%-VALU_PUSH").press()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]"
        ).text = "E602"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]"
        ).text = "E902"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]"
        ).text = "EBR2"
        session.findById("wnd[1]").sendVKey(0)
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        # Tipos de documento
        session.findById("wnd[0]/usr/btn%_S_BSART_%_APP_%-VALU_PUSH").press()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]"
        ).text = "ZUB"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]"
        ).text = "UB"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]"
        ).text = "YIMP"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]"
        ).text = "YNAC"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]"
        ).text = "NB"
        session.findById("wnd[1]").sendVKey(0)
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        session.findById("wnd[0]/usr/ctxtLISTU").text = "ALV"
        session.findById("wnd[0]/usr/ctxtLISTU").setFocus()
        session.findById("wnd[0]/usr/ctxtLISTU").caretPosition = 3
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        # Exportação
        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()

        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except:
            pass

        nome_arquivo = f"{data_nome_arquivo} {files[0]}"

        print(f"Exportando ME2W para: {path_compras}")
        print(f"Nome do arquivo ME2W: {nome_arquivo}")

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = path_compras
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        print(f"Enviando ME2W para o MinIO: tmp/{nome_arquivo}")

        arquivo = minio.buffer_creator(path_compras, nome_arquivo)
        minio.upload_from_bytesIO(arquivo, "tmp", nome_arquivo)

        sap.encerrar_sap()

        print("Extração da ME2W concluída.")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO 2 :: ME5A - REQUISIÇÕES DE COMPRA
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def bloco_me5a():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        print("Iniciando extração da ME5A!")

        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ME5A"
        session.findById("wnd[0]").sendVKey(0)

        # Plantas
        session.findById("wnd[0]/usr/btn%_S_WERKS_%_APP_%-VALU_PUSH").press()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]"
        ).text = "P60*"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]"
        ).text = "E60*"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]"
        ).text = "E90*"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]"
        ).text = "P90*"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]"
        ).text = "E89*"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        # Tipos de documento
        session.findById("wnd[0]/usr/ctxtS_BSART-LOW").setFocus()
        session.findById("wnd[0]/usr/btn%_S_BSART_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]").sendVKey(2)
        session.findById("wnd[2]").close()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]"
        ).text = "YES2"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]"
        ).text = "YES4"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        session.findById("wnd[0]/usr/chkP_ZUGBA").selected = True
        session.findById("wnd[0]/usr/chkP_MEMORY").selected = True
        session.findById("wnd[0]/usr/chkP_ERLBA").selected = True
        session.findById("wnd[0]/usr/chkP_BSTBA").selected = True
        session.findById("wnd[0]/usr/chkP_SELGS").selected = True
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        # Exportação
        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()

        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except:
            pass

        nome_arquivo = f"{data_nome_arquivo} {files[1]}"

        print(f"Exportando ME5A para: {path_compras}")
        print(f"Nome do arquivo ME5A: {nome_arquivo}")

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = path_compras
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        print(f"Enviando ME5A para o MinIO: tmp/{nome_arquivo}")

        arquivo = minio.buffer_creator(path_compras, nome_arquivo)
        minio.upload_from_bytesIO(arquivo, "tmp", nome_arquivo)

        sap.encerrar_sap()

        print("Extração da ME5A concluída.")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO 3 :: SE16N - EBAN
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def bloco_eban():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        print("Iniciando extração da tabela EBAN!")

        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nSE16N"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "EBAN"
        session.findById("wnd[0]/usr/ctxtGD-TAB").caretPosition = 4
        session.findById("wnd[0]").sendVKey(0)

        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 1
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 2
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").press()

        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]"
        ).text = "YES2"
        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]"
        ).text = "YES4"
        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]"
        ).text = "NB"

        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton(
            "&MB_EXPORT"
        )
        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem(
            "&XXL"
        )
        session.findById("wnd[1]").sendVKey(4)

        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except:
            pass

        nome_arquivo = files[2]

        print(f"Exportando EBAN para: {path_tabelas}")
        print(f"Nome do arquivo EBAN: {nome_arquivo}")

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = path_tabelas
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 20
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        print(f"Enviando EBAN para o MinIO: tmp/{nome_arquivo}")

        arquivo = minio.buffer_creator(path_tabelas, nome_arquivo)
        minio.upload_from_bytesIO(arquivo, "tmp", nome_arquivo)

        sap.encerrar_sap()

        print("Extração EBAN concluída.")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO 4 :: SE16N - EKKO
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def bloco_ekko():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        print("Iniciando extração da tabela EKKO!")

        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "EKKO"
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").setFocus()

        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 1
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 2
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,2]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,2]").press()

        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]"
        ).text = "NB"
        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]"
        ).text = "YIMP"
        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]"
        ).text = "YNAC"
        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,3]"
        ).text = "ZUB"
        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,4]"
        ).text = "ZUVR"

        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

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

        nome_arquivo = files[3]

        print(f"Exportando EKKO para: {path_tabelas}")
        print(f"Nome do arquivo EKKO: {nome_arquivo}")

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = path_tabelas
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        print(f"Enviando EKKO para o MinIO: tmp/{nome_arquivo}")

        arquivo = minio.buffer_creator(path_tabelas, nome_arquivo)
        minio.upload_from_bytesIO(arquivo, "tmp", nome_arquivo)

        sap.encerrar_sap()

        print("Extração EKKO concluída.")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO 5 :: SE16N - EKPO
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def bloco_ekpo():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        print("Iniciando extração da tabela EKPO!")

        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "EKPO"
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]").sendVKey(0)

        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 1
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 2
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 3
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 4
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 5
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 6
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,2]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,2]").press()

        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]"
        ).text = "1000000000"
        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]"
        ).text = "2000000000"
        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]"
        ).text = "4000000000"
        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,0]"
        ).text = "1999999999"
        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,1]"
        ).text = "2999999999"
        session.findById(
            "wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,2]"
        ).text = "4999999999"

        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

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

        nome_arquivo = files[4]

        print(f"Exportando EKPO para: {path_tabelas}")
        print(f"Nome do arquivo EKPO: {nome_arquivo}")

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = path_tabelas
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        print(f"Enviando EKPO para o MinIO: tmp/{nome_arquivo}")

        arquivo = minio.buffer_creator(path_tabelas, nome_arquivo)
        minio.upload_from_bytesIO(arquivo, "tmp", nome_arquivo)

        sap.encerrar_sap()

        print("Extração EKPO concluída.")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO 6 :: ZMM_PURDOCS_REPORT
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def bloco_zmm_purdocs_report():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        print("Iniciando extração ZMM_PURDOCS_REPORT!")

        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZMM_PURDOCS_REPORT"
        session.findById("wnd[0]").sendVKey(0)

        # Organização de compras
        session.findById("wnd[0]/usr/btn%_SO_EKORG_%_APP_%-VALU_PUSH").press()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]"
        ).text = "E602"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]"
        ).text = "E902"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]"
        ).text = "EBR2"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]"
        ).setFocus()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]"
        ).caretPosition = 4
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        # Tipos de documento
        session.findById("wnd[0]/usr/btn%_SO_BSART_%_APP_%-VALU_PUSH").press()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]"
        ).text = "YIMP"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]"
        ).text = "YNAC"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]"
        ).text = "NB"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]"
        ).text = "MK"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]"
        ).setFocus()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]"
        ).caretPosition = 2
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        # Plantas
        session.findById("wnd[0]/usr/btn%_SO_WERKS_%_APP_%-VALU_PUSH").press()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]"
        ).text = "P6*"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]"
        ).text = "P9*"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]"
        ).text = "E89*"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]"
        ).text = "E6*"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]"
        ).text = "E9*"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]"
        ).setFocus()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]"
        ).caretPosition = 3
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        session.findById("wnd[0]/usr/ctxtP_LAYOUT").text = "/DATAINSIGHT"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except:
            pass

        session.findById(
            "wnd[0]/usr/cntlGRID/shellcont/shell/shellcont[0]/shell/shellcont[1]/shell"
        ).pressButton("&XXL")

        nome_arquivo = f"{data_nome_arquivo} {files[5]}"

        print(f"Exportando ZMM_PURDOCS_REPORT para: {path_compras}")
        print(f"Nome do arquivo ZMM_PURDOCS_REPORT: {nome_arquivo}")

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = path_compras
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        print(f"Enviando ZMM_PURDOCS_REPORT para o MinIO: tmp/{nome_arquivo}")

        arquivo = minio.buffer_creator(path_compras, nome_arquivo)
        minio.upload_from_bytesIO(arquivo, "tmp", nome_arquivo)

        sap.encerrar_sap()

        print("Extração ZMM_PURDOCS_REPORT concluída.")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO 7 :: ZMM_PURDOCS_REPORT - HEADER TEXT
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def bloco_zmm_purdocs_header_text():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        print("Iniciando extração ZMM_PURDOCS_REPORT - HEADER TEXT!")

        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nZMM_PURDOCS_REPORT"
        session.findById("wnd[0]").sendVKey(0)

        session.findById("wnd[0]/usr/btn%_SO_EKORG_%_APP_%-VALU_PUSH").press()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]"
        ).text = "E602"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]"
        ).text = "E902"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]"
        ).text = "EBR2"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]"
        ).setFocus()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]"
        ).caretPosition = 4
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        session.findById("wnd[0]/usr/btn%_SO_BSART_%_APP_%-VALU_PUSH").press()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]"
        ).text = "YIMP"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]"
        ).text = "YNAC"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]"
        ).text = "NB"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]"
        ).text = "MK"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]"
        ).setFocus()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]"
        ).caretPosition = 2
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        session.findById("wnd[0]/usr/btn%_SO_WERKS_%_APP_%-VALU_PUSH").press()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]"
        ).text = "P9*"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]"
        ).text = "E9*"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]"
        ).setFocus()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]"
        ).caretPosition = 3
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        session.findById("wnd[0]/usr/chkP_LONGT").selected = True
        session.findById("wnd[0]/usr/chkP_LONGT2").selected = True
        session.findById("wnd[0]/usr/chkP_LONGT3").selected = True
        session.findById("wnd[0]/usr/ctxtP_LAYOUT").text = "/HDTXT"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except:
            pass

        session.findById(
            "wnd[0]/usr/cntlGRID/shellcont/shell/shellcont[0]/shell/shellcont[1]/shell"
        ).pressButton("&XXL")

        nome_arquivo = f"{data_nome_arquivo} {files[6]}"

        print(f"Exportando HEADER TEXT para: {path_compras}")
        print(f"Nome do arquivo HEADER TEXT: {nome_arquivo}")

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = path_compras
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        print(f"Enviando HEADER TEXT para o MinIO: tmp/{nome_arquivo}")

        arquivo = minio.buffer_creator(path_compras, nome_arquivo)
        minio.upload_from_bytesIO(arquivo, "tmp", nome_arquivo)

        sap.encerrar_sap()

        print("Textos de Cabeçalho extraídos com sucesso.")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO 8 :: ZMM_PURDOCS_REPORT - AUXINFO
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def bloco_zmm_purdocs_auxinfo():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        print("Iniciando extração ZMM_PURDOCS_REPORT - INFORMAÇÕES AUXILIARES!")

        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZMM_PURDOCS_REPORT"
        session.findById("wnd[0]").sendVKey(0)

        session.findById("wnd[0]/usr/btn%_SO_EKORG_%_APP_%-VALU_PUSH").press()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]"
        ).text = "E602"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]"
        ).text = "E902"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]"
        ).text = "EBR2"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]"
        ).setFocus()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]"
        ).caretPosition = 4
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        session.findById("wnd[0]/usr/btn%_SO_BSART_%_APP_%-VALU_PUSH").press()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]"
        ).text = "YIMP"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]"
        ).text = "YNAC"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]"
        ).text = "NB"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]"
        ).text = "MK"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]"
        ).setFocus()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]"
        ).caretPosition = 2
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        session.findById("wnd[0]/usr/btn%_SO_WERKS_%_APP_%-VALU_PUSH").press()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]"
        ).text = "P6*"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]"
        ).text = "P9*"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]"
        ).text = "E89*"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]"
        ).text = "E6*"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]"
        ).text = "E9*"
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]"
        ).setFocus()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]"
        ).caretPosition = 3
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        session.findById("wnd[0]/usr/chkP_LONGT").selected = True
        session.findById("wnd[0]/usr/chkP_LONGT2").selected = True
        session.findById("wnd[0]/usr/chkP_LONGT3").selected = True
        session.findById("wnd[0]/usr/ctxtP_LAYOUT").text = "/AUXINFO"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except:
            pass

        session.findById(
            "wnd[0]/usr/cntlGRID/shellcont/shell/shellcont[0]/shell/shellcont[1]/shell"
        ).pressButton("&XXL")

        nome_arquivo = f"{data_nome_arquivo} {files[7]}"

        print(f"Exportando AUXINFO para: {path_compras}")
        print(f"Nome do arquivo AUXINFO: {nome_arquivo}")

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = path_compras
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        print(f"Enviando AUXINFO para o MinIO: tmp/{nome_arquivo}")

        arquivo = minio.buffer_creator(path_compras, nome_arquivo)
        minio.upload_from_bytesIO(arquivo, "tmp", nome_arquivo)

        sap.encerrar_sap()

        print("Informações auxiliares extraídas com sucesso.")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # EXECUÇÃO DOS BLOCOS COM RETRY
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    print(" ---------- Iniciando bloco 1 :: ME2W ---------- ")
    executar_com_retry(erros, "ME2W", bloco_me2w, tentativas=3, intervalo=60)
    print(" ---------- Bloco 1 :: ME2W finalizado ---------- ")

    print(" ---------- Iniciando bloco 2 :: ME5A ---------- ")
    executar_com_retry(erros, "ME5A", bloco_me5a, tentativas=3, intervalo=60)
    print(" ---------- Bloco 2 :: ME5A finalizado ---------- ")

    print(" ---------- Iniciando bloco 3 :: EBAN ---------- ")
    executar_com_retry(erros, "EBAN", bloco_eban, tentativas=3, intervalo=60)
    print(" ---------- Bloco 3 :: EBAN finalizado ---------- ")

    print(" ---------- Iniciando bloco 4 :: EKKO ---------- ")
    executar_com_retry(erros, "EKKO", bloco_ekko, tentativas=3, intervalo=60)
    print(" ---------- Bloco 4 :: EKKO finalizado ---------- ")

    print(" ---------- Iniciando bloco 5 :: EKPO ---------- ")
    executar_com_retry(erros, "EKPO", bloco_ekpo, tentativas=3, intervalo=60)
    print(" ---------- Bloco 5 :: EKPO finalizado ---------- ")

    print(" ---------- Iniciando bloco 6 :: ZMM_PURDOCS_REPORT ---------- ")
    executar_com_retry(
        erros,
        "ZMM_PURDOCS_REPORT",
        bloco_zmm_purdocs_report,
        tentativas=3,
        intervalo=60,
    )
    print(" ---------- Bloco 6 :: ZMM_PURDOCS_REPORT finalizado ---------- ")

    print(" ---------- Iniciando bloco 7 :: ZMM_PURDOCS_REPORT - HEADER TEXT ---------- ")
    executar_com_retry(
        erros,
        "ZMM_PURDOCS_HEADERTEXT",
        bloco_zmm_purdocs_header_text,
        tentativas=3,
        intervalo=60,
    )
    print(" ---------- Bloco 7 :: ZMM_PURDOCS_REPORT - HEADER TEXT finalizado ---------- ")

    print(" ---------- Iniciando bloco 8 :: ZMM_PURDOCS_REPORT - AUXINFO ---------- ")
    executar_com_retry(
        erros,
        "ZMM_PURDOCS_AUXINFO",
        bloco_zmm_purdocs_auxinfo,
        tentativas=3,
        intervalo=60,
    )
    print(" ---------- Bloco 8 :: ZMM_PURDOCS_REPORT - AUXINFO finalizado ---------- ")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # VALIDAÇÃO FINAL DA EXECUÇÃO
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    time.sleep(10)

    if erros:
        raise RuntimeError(
            "Ocorreram erros em uma ou mais extrações de compras:\n"
            + "\n".join(erros)
        )

    print(" ---------- Extração SAP4HANA :: Compras concluída com sucesso! ---------- ")


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# EXECUÇÃO DIRETA DO SCRIPT
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
if __name__ == "__main__":
    engdds_compras_main()