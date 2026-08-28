# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# IMPORTAR BIBLIOTECAS
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# Bibliotecas :: Gerais
import logging
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
    Registra erro de uma etapa sem interromper imediatamente o script.

    A ideia é permitir que as próximas extrações sejam tentadas e,
    somente ao final, sinalizar ao Menestrel que houve falha parcial.
    """
    mensagem = f"{etapa} :: {str(erro)}"

    print(f"Erro na etapa {etapa}: {str(erro)}")
    erros.append(mensagem)

    try:
        sap.encerrar_sap()
    except:
        pass


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# INICIANDO PROCESSAMENTO :: EXTRAÇÃO SAP4HANA SKU
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def engdds_sku_main():
    """
    Executa as extrações de SKU no SAP S/4HANA.

    Fluxo:
        1. Carrega os metadados do files.json.
        2. Extrai a tabela MARA via SE16N.
        3. Extrai a tabela MAKT via SE16N.
        4. Extrai a visão/tabela ZVMM_MAT_CLASS via SE16N.
        5. Envia os arquivos gerados para o bucket tmp do MinIO.

    Observação:
        As etapas são independentes. Se uma falhar, o script tenta executar
        as próximas e só informa falha ao Menestrel no final.
    """
    print(" ---------- Iniciando extração SAP4HANA :: SKU ---------- ")

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

    path_sku = meta_arquivos["engdds_sku.py"]["path"]
    files = meta_arquivos["engdds_sku.py"]["files"]

    print(f"Path configurado para arquivos SKU: {path_sku}")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO 1 :: SE16N - MARA
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    print(" ---------- Iniciando bloco 1 :: MARA ---------- ")

    try:
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        print("Iniciando extração da tabela MARA...")

        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "MARA"
        session.findById("wnd[0]/usr/ctxtGD-TAB").caretPosition = 4
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]").sendVKey(18)

        # Filtro de materiais por faixa de código
        print("Aplicando filtros de materiais para MARA...")

        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").press()

        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC").columns.elementAt(1).width = 31
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = "1000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = "2000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]").text = "4000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,3]").text = "7000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,0]").text = "1999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,1]").text = "2999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,2]").text = "4999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").text = "7999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").setFocus()
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").caretPosition = 10
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        print("Executando consulta MARA...")

        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        # Exportação
        print("Preparando exportação da MARA para XLSX...")

        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")
        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem("&XXL")

        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except:
            pass

        session.findById("wnd[1]/usr/ctxtDY_PATH").setFocus()
        session.findById("wnd[1]/usr/ctxtDY_PATH").caretPosition = 0
        session.findById("wnd[1]").sendVKey(4)

        nome_arquivo = files[0]

        print(f"Exportando MARA para: {path_sku}")
        print(f"Nome do arquivo MARA: {nome_arquivo}")

        session.findById("wnd[2]/usr/ctxtDY_PATH").text = path_sku
        session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[2]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[2]/tbar[0]/btn[11]").press()
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        print(f"Enviando MARA para o MinIO: tmp/{nome_arquivo}")

        arquivo = minio.buffer_creator(path_sku, nome_arquivo)
        minio.upload_from_bytesIO(arquivo, "tmp", nome_arquivo)

        sap.encerrar_sap()

        print("Extração MARA concluída.")

    except Exception as e:
        registrar_erro(erros, "MARA", e)

    print(" ---------- Bloco 1 :: MARA finalizado ---------- ")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO 2 :: SE16N - MAKT
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    print(" ---------- Iniciando bloco 2 :: MAKT ---------- ")

    try:
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        print("Iniciando extração da tabela MAKT...")

        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "MAKT"
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]").sendVKey(18)

        # Filtro de materiais por faixa de código
        print("Aplicando filtros de materiais para MAKT...")

        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").press()

        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = "1000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = "2000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]").text = "4000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,3]").text = "7000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,0]").text = "1999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,1]").text = "2999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,2]").text = "4999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").text = "7999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").setFocus()
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").caretPosition = 10
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        print("Executando consulta MAKT...")

        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").firstVisibleRow = 36

        # Exportação
        print("Preparando exportação da MAKT para XLSX...")

        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")
        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem("&XXL")

        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except:
            pass

        nome_arquivo = files[1]

        print(f"Exportando MAKT para: {path_sku}")
        print(f"Nome do arquivo MAKT: {nome_arquivo}")

        try:
            session.findById("wnd[2]/usr/ctxtDY_PATH").text = path_sku
            session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = nome_arquivo
        except:
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = path_sku
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo

        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[1]/tbar[0]/btn[11]").press()
        session.findById("wnd[0]/tbar[0]/btn[15]").press()
        session.findById("wnd[0]/tbar[0]/btn[15]").press()

        print(f"Enviando MAKT para o MinIO: tmp/{nome_arquivo}")

        arquivo = minio.buffer_creator(path_sku, nome_arquivo)
        minio.upload_from_bytesIO(arquivo, "tmp", nome_arquivo)

        sap.encerrar_sap()

        print("Extração MAKT concluída.")

    except Exception as e:
        registrar_erro(erros, "MAKT", e)

    print(" ---------- Bloco 2 :: MAKT finalizado ---------- ")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO 3 :: SE16N - ZVMM_MAT_CLASS
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    print(" ---------- Iniciando bloco 3 :: ZVMM_MAT_CLASS ---------- ")

    try:
        session = sap.login_to_s4hana()

        print("Login ao SAP S/4HANA realizado com sucesso.")

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        print("Iniciando extração da tabela ZVMM_MAT_CLASS...")

        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "ZVMM_MAT_CLASS"
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]").sendVKey(18)

        # Filtro de materiais por faixa de código
        print("Aplicando filtros de materiais para ZVMM_MAT_CLASS...")

        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").press()

        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = "1000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = "2000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]").text = "4000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,3]").text = "7000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,0]").text = "1999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,1]").text = "2999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,2]").text = "4999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").text = "7999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").setFocus()
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").caretPosition = 10
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        print("Executando consulta ZVMM_MAT_CLASS...")

        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").firstVisibleRow = 36

        # Exportação
        print("Preparando exportação da ZVMM_MAT_CLASS para XLSX...")

        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")
        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem("&XXL")

        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except:
            pass

        nome_arquivo = files[2]

        print(f"Exportando ZVMM_MAT_CLASS para: {path_sku}")
        print(f"Nome do arquivo ZVMM_MAT_CLASS: {nome_arquivo}")

        try:
            session.findById("wnd[2]/usr/ctxtDY_PATH").text = path_sku
            session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = nome_arquivo
        except:
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = path_sku
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo

        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        print(f"Enviando ZVMM_MAT_CLASS para o MinIO: tmp/{nome_arquivo}")

        arquivo = minio.buffer_creator(path_sku, nome_arquivo)
        minio.upload_from_bytesIO(arquivo, "tmp", nome_arquivo)

        sap.encerrar_sap()

        print("Extração ZVMM_MAT_CLASS concluída.")

    except Exception as e:
        registrar_erro(erros, "ZVMM_MAT_CLASS", e)

    print(" ---------- Bloco 3 :: ZVMM_MAT_CLASS finalizado ---------- ")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # VALIDAÇÃO FINAL DA EXECUÇÃO
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    time.sleep(10)

    if erros:
        raise RuntimeError(
            "Ocorreram erros em uma ou mais extrações de SKU:\n"
            + "\n".join(erros)
        )

    print(" ---------- Extração SAP4HANA :: SKU concluída com sucesso! ---------- ")


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# EXECUÇÃO DIRETA DO SCRIPT
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
if __name__ == "__main__":
    engdds_sku_main()