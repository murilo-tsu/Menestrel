
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# IMPORTAR BIBLIOTECAS
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

# Bibliotecas :: Gerais
from datetime import date, timedelta
import json
import time
import os

# Bibliotecas :: Excel
import win32com.client

# Bibliotecas :: Específicas
from saplogin import SAPLogin
from Minio import MinioConnector


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# CONFIGURAÇÃO DE EXECUÇÃO
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

# True  = executa backfill desde DATA_INICIAL_BACKFILL até D-1
#
# False = executa rotina normal:
#         - Sempre D-1
MODO_BACKFILL = False

# Data inicial do backfill
#
# Exemplo:
# date(2026, 7, 1)  -> 01/07/2026
# date(2026, 1, 1)  -> 01/01/2026
DATA_INICIAL_BACKFILL = date(2026, 1, 31)


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# FUNÇÕES AUXILIARES
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def datas_para_processar():
    """
    Define as datas que serão extraídas.

    MODO_BACKFILL = True:
        Processa todas as datas desde DATA_INICIAL_BACKFILL até D-1.

    MODO_BACKFILL = False:
        Processa somente D-1.

    O dia atual nunca é processado.
    """

    hoje = date.today()

    # O dia atual nunca é processado
    data_final = hoje - timedelta(days=1)

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # MODO BACKFILL
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    if MODO_BACKFILL:

        data_inicial = DATA_INICIAL_BACKFILL

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # MODO NORMAL
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    else:

        data_inicial = data_final

    # Validação
    if data_inicial > data_final:

        raise ValueError(
            f"Data inicial {data_inicial} é maior que "
            f"a data final {data_final}."
        )

    return [
        data_inicial + timedelta(days=i)
        for i in range(
            (data_final - data_inicial).days + 1
        )
    ]


def data_sap(data_ref):
    """
    Converte a data de referência para o formato esperado pelo SAP.

    Exemplo:
        2026-08-31 -> 31.08.2026
    """

    return data_ref.strftime("%d.%m.%Y")


def nome_arquivo_mb5b(data_ref):
    """
    Monta o nome do arquivo de saída.

    Padrão:
        MB5B_AAAAMMDD.XLSX

    Exemplo:
        2026-08-31 -> MB5B_20260831.XLSX
    """

    return f"MB5B_{data_ref:%Y%m%d}.XLSX"


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# SAP :: FUNÇÕES AUXILIARES
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def abrir_mb5b(session):
    """
    Abre/reabre a transação MB5B utilizando a sessão SAP atual.

    Utiliza /nMB5B para reiniciar a transação sem fechar
    a sessão SAP.
    """

    session.findById(
        "wnd[0]/tbar[0]/okcd"
    ).text = "/nMB5B"

    session.findById(
        "wnd[0]"
    ).sendVKey(0)

    time.sleep(2)


def parametrizar_mb5b(session, data_formatada):
    """
    Parametriza a transação MB5B para a data informada.

    Mantém a mesma parametrização da rotina original.
    """

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # LISTA RESUMIDA
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    session.findById(
        "wnd[0]/usr/chkPA_SUMFL"
    ).selected = True


    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # EMPRESA
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    session.findById(
        "wnd[0]/usr/ctxtBUKRS-LOW"
    ).text = "E900"


    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # DATA INICIAL
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    session.findById(
        "wnd[0]/usr/ctxtDATUM-LOW"
    ).text = data_formatada


    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # DATA FINAL
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    session.findById(
        "wnd[0]/usr/ctxtDATUM-HIGH"
    ).text = data_formatada


    session.findById(
        "wnd[0]/usr/chkPA_SUMFL"
    ).setFocus()


def selecionar_campo_mb5b(session):
    """
    Executa a seleção do campo utilizada pela rotina original.
    """

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # SELEÇÃO DO CAMPO
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    session.findById(
        "wnd[0]/tbar[1]/btn[32]"
    ).press()


    session.findById(
        "wnd[1]/usr/tblSAPLSKBHTC_FIELD_LIST"
    ).getAbsoluteRow(1).selected = True


    session.findById(
        "wnd[1]/usr/tblSAPLSKBHTC_FIELD_LIST/"
        "txtGT_FIELD_LIST-SELTEXT[0,1]"
    ).setFocus()


    session.findById(
        "wnd[1]/usr/tblSAPLSKBHTC_FIELD_LIST/"
        "txtGT_FIELD_LIST-SELTEXT[0,1]"
    ).caretPosition = 0


    session.findById(
        "wnd[1]/usr/btnAPP_WL_SING"
    ).press()


    session.findById(
        "wnd[1]/tbar[0]/btn[0]"
    ).press()


def executar_mb5b(session):
    """
    Executa a transação MB5B.
    """

    session.findById(
        "wnd[0]/tbar[1]/btn[8]"
    ).press()


def exportar_mb5b(session, pasta_destino, nome_arquivo):
    """
    Exporta o resultado da MB5B para Excel.
    """

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # EXPORTAÇÃO PARA EXCEL
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    session.findById(
        "wnd[0]/tbar[1]/btn[43]"
    ).press()


    session.findById(
        "wnd[1]/tbar[0]/btn[0]"
    ).press()


    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # DEFINE PASTA
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    session.findById(
        "wnd[1]/usr/ctxtDY_PATH"
    ).text = pasta_destino


    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # DEFINE NOME
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    session.findById(
        "wnd[1]/usr/ctxtDY_FILENAME"
    ).text = nome_arquivo


    session.findById(
        "wnd[1]/usr/ctxtDY_FILENAME"
    ).caretPosition = len(
        nome_arquivo
    )


    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # SALVA
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    session.findById(
        "wnd[1]/tbar[0]/btn[0]"
    ).press()


def fechar_excel_mb5b():
    """
    Fecha o Excel utilizado pela exportação da MB5B.

    Primeiro tenta fechar via COM.
    Depois utiliza taskkill como garantia para liberar
    a memória antes da próxima extração.

    ATENÇÃO:
        taskkill encerra todas as instâncias EXCEL.EXE
        existentes na máquina.
    """

    print(
        "Iniciando fechamento do Excel..."
    )

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # TENTATIVA 1 :: COM
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    try:

        excel = win32com.client.GetActiveObject(
            "Excel.Application"
        )

        print(
            "Instância do Excel encontrada via COM."
        )

        workbooks = list(
            excel.Workbooks
        )

        for workbook in workbooks:

            try:

                nome_workbook = workbook.Name

                print(
                    f"Workbook encontrado :: "
                    f"{nome_workbook}"
                )

                if nome_workbook.upper().startswith("MB5B"):

                    print(
                        f"Fechando workbook :: "
                        f"{nome_workbook}"
                    )

                    workbook.Close(
                        SaveChanges=False
                    )

            except Exception as erro:

                print(
                    "Erro ao fechar workbook :: "
                    f"{str(erro)}"
                )


        # Tenta encerrar a instância caso não existam
        # mais workbooks.
        try:

            if excel.Workbooks.Count == 0:

                excel.Quit()

                print(
                    "Instância do Excel encerrada via COM."
                )

        except Exception as erro:

            print(
                "Não foi possível encerrar o Excel via COM :: "
                f"{str(erro)}"
            )


    except Exception as erro:

        print(
            "Não foi possível localizar o Excel via COM."
        )

        print(
            f"Detalhe :: {str(erro)}"
        )


    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # AGUARDA
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    time.sleep(2)


    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # TENTATIVA 2 :: TASKKILL
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    try:

        resultado = os.system(
            'taskkill /F /IM EXCEL.EXE >nul 2>&1'
        )

        if resultado == 0:

            print(
                "EXCEL.EXE encerrado com sucesso."
            )

        else:

            print(
                "Nenhum EXCEL.EXE ativo para encerrar."
            )

    except Exception as erro:

        print(
            "Erro ao executar taskkill do Excel :: "
            f"{str(erro)}"
        )


    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # AGUARDA LIBERAÇÃO DE MEMÓRIA
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    time.sleep(3)

    print(
        "Excel liberado."
    )


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# INSTANCIANDO VARIÁVEIS DE AMBIENTE :: SAP
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

sap = SAPLogin()


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# INICIANDO PROCESSAMENTO :: EXTRAÇÃO SAP4HANA MB5B
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def engdds_mb5b_main():

    minio = MinioConnector()


    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # CARREGANDO METADADOS DOS ARQUIVOS
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    script_dir = os.path.dirname(
        os.path.abspath(__file__)
    )


    files_json_path = os.path.join(
        script_dir,
        "files.json"
    )


    with open(
        files_json_path,
        "r",
        encoding="utf-8"
    ) as file:

        meta_arquivos = json.load(file)


    # Chave correta do files.json
    pasta_destino = meta_arquivos[
        "engdds_mb5b.py"
    ][
        "path"
    ]


    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # GARANTE QUE A PASTA LOCAL EXISTA
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    os.makedirs(
        pasta_destino,
        exist_ok=True
    )


    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # DEFINE DATAS
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    datas = datas_para_processar()

    erros = []


    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # LOG DAS DATAS
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    print()
    print(
        "=" * 80
    )

    print(
        "DATAS PROGRAMADAS PARA EXTRAÇÃO"
    )

    print(
        "=" * 80
    )

    print(
        f"Modo backfill :: {MODO_BACKFILL}"
    )

    print(
        f"Primeira data :: "
        f"{datas[0].strftime('%d/%m/%Y')}"
    )

    print(
        f"Última data :: "
        f"{datas[-1].strftime('%d/%m/%Y')}"
    )

    print(
        f"Total de datas :: {len(datas)}"
    )

    print(
        "=" * 80
    )


    # ==========================================================================
    # MODO BACKFILL
    # ==========================================================================

    if MODO_BACKFILL:

        session = None

        try:

            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            # LOGIN ÚNICO NO SAP
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

            print()
            print(
                "Abrindo sessão SAP para o backfill..."
            )

            session = sap.login_to_s4hana()


            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            # ABRE MB5B
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

            abrir_mb5b(
                session
            )


            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            # LOOP DO BACKFILL
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

            for indice, data_ref in enumerate(
                datas,
                start=1
            ):

                data_formatada = data_sap(
                    data_ref
                )

                nome_arquivo = nome_arquivo_mb5b(
                    data_ref
                )

                caminho_arquivo_local = os.path.join(
                    pasta_destino,
                    nome_arquivo
                )


                print()
                print(
                    "=" * 80
                )

                print(
                    f"[{indice}/{len(datas)}] "
                    f"PROCESSANDO MB5B :: "
                    f"{data_formatada}"
                )

                print(
                    f"Arquivo :: {nome_arquivo}"
                )

                print(
                    "=" * 80
                )


                try:

                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                    # PARAMETRIZAÇÃO
                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                    parametrizar_mb5b(
                        session,
                        data_formatada
                    )


                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                    # EXECUTA
                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                    executar_mb5b(
                        session
                    )


                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                    # SELEÇÃO DO CAMPO
                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                    selecionar_campo_mb5b(
                        session
                    )


                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                    # EXPORTAÇÃO
                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                    exportar_mb5b(
                        session,
                        pasta_destino,
                        nome_arquivo
                    )


                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                    # AGUARDA ARQUIVO
                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                    print(
                        f"Aguardando arquivo local :: "
                        f"{caminho_arquivo_local}"
                    )


                    arquivo_encontrado = False


                    for tentativa in range(30):

                        if os.path.exists(
                            caminho_arquivo_local
                        ):

                            arquivo_encontrado = True

                            break

                        time.sleep(1)


                    if not arquivo_encontrado:

                        raise FileNotFoundError(
                            "Arquivo não encontrado após "
                            "exportação SAP: "
                            f"{caminho_arquivo_local}"
                        )


                    print(
                        f"Arquivo encontrado :: "
                        f"{caminho_arquivo_local}"
                    )


                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                    # PREPARA ARQUIVO
                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                    arquivo = minio.buffer_creator(
                        pasta_destino,
                        nome_arquivo
                    )


                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                    # ENVIA PARA MINIO
                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                    minio.upload_from_bytesIO(
                        arquivo,
                        "tmp",
                        nome_arquivo
                    )


                    print(
                        f"MB5B gravado no bucket tmp "
                        f"como {nome_arquivo}"
                    )


                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                    # FECHA EXCEL
                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                    print()
                    print(
                        ">>> FECHANDO EXCEL <<<"
                    )

                    fechar_excel_mb5b()


                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                    # PREPARA PRÓXIMA DATA
                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                    if indice < len(datas):

                        print()
                        print(
                            ">>> REINICIANDO MB5B <<<"
                        )

                        abrir_mb5b(
                            session
                        )


                except Exception as erro:

                    print()
                    print(
                        "Erro ao processar MB5B"
                    )

                    print(
                        f"Data :: {data_formatada}"
                    )

                    print(
                        f"Mensagem :: {str(erro)}"
                    )


                    erros.append(
                        f"{data_formatada} -> {str(erro)}"
                    )


                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                    # FECHA EXCEL EM CASO DE ERRO
                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                    try:

                        fechar_excel_mb5b()

                    except:

                        pass


                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                    # TENTA RECUPERAR MB5B
                    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                    if indice < len(datas):

                        try:

                            print(
                                "Tentando recuperar MB5B..."
                            )

                            abrir_mb5b(
                                session
                            )

                        except Exception as erro_retorno:

                            print(
                                "Não foi possível recuperar MB5B :: "
                                f"{str(erro_retorno)}"
                            )


        except Exception as erro_sessao:

            mensagem = (
                "Erro ao iniciar/manter a sessão SAP "
                "durante o backfill :: "
                f"{str(erro_sessao)}"
            )

            print(
                mensagem
            )

            erros.append(
                mensagem
            )


        finally:

            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            # FECHA EXCEL POR SEGURANÇA
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

            try:

                fechar_excel_mb5b()

            except:

                pass


            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            # FECHA SAP SOMENTE NO FINAL
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

            try:

                sap.encerrar_sap()

            except:

                pass


    # ==========================================================================
    # MODO NORMAL
    # ==========================================================================

    else:

        for data_ref in datas:

            data_formatada = data_sap(
                data_ref
            )

            nome_arquivo = nome_arquivo_mb5b(
                data_ref
            )

            caminho_arquivo_local = os.path.join(
                pasta_destino,
                nome_arquivo
            )


            print()
            print(
                "=" * 80
            )

            print(
                f"PROCESSANDO MB5B :: "
                f"{data_formatada}"
            )

            print(
                f"Arquivo :: {nome_arquivo}"
            )

            print(
                "=" * 80
            )


            try:

                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                # LOGIN SAP
                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                session = sap.login_to_s4hana()


                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                # ACESSA MB5B
                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                abrir_mb5b(
                    session
                )


                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                # PARAMETRIZAÇÃO
                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                parametrizar_mb5b(
                    session,
                    data_formatada
                )


                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                # EXECUTA
                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                executar_mb5b(
                    session
                )


                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                # SELEÇÃO DO CAMPO
                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                selecionar_campo_mb5b(
                    session
                )


                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                # EXPORTAÇÃO
                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                exportar_mb5b(
                    session,
                    pasta_destino,
                    nome_arquivo
                )


                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                # AGUARDA ARQUIVO
                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                print(
                    f"Aguardando arquivo local :: "
                    f"{caminho_arquivo_local}"
                )


                arquivo_encontrado = False


                for tentativa in range(30):

                    if os.path.exists(
                        caminho_arquivo_local
                    ):

                        arquivo_encontrado = True

                        break

                    time.sleep(1)


                if not arquivo_encontrado:

                    raise FileNotFoundError(
                        "Arquivo não encontrado após "
                        "exportação SAP: "
                        f"{caminho_arquivo_local}"
                    )


                print(
                    f"Arquivo encontrado :: "
                    f"{caminho_arquivo_local}"
                )


                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                # PREPARA ARQUIVO
                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                arquivo = minio.buffer_creator(
                    pasta_destino,
                    nome_arquivo
                )


                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                # ENVIA PARA MINIO
                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                minio.upload_from_bytesIO(
                    arquivo,
                    "tmp",
                    nome_arquivo
                )


                print(
                    f"MB5B gravado no bucket tmp "
                    f"como {nome_arquivo}"
                )


                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                # FECHA EXCEL
                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                fechar_excel_mb5b()


            except Exception as erro:

                erros.append(
                    f"{data_formatada} -> {str(erro)}"
                )


                print(
                    "Erro ao processar MB5B"
                )


                print(
                    f"Data :: {data_formatada}"
                )


                print(
                    f"Mensagem :: {str(erro)}"
                )


            finally:

                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                # FECHA EXCEL
                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                try:

                    fechar_excel_mb5b()

                except:

                    pass


                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                # ENCERRA SAP
                # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

                try:

                    sap.encerrar_sap()

                except:

                    pass


                time.sleep(10)


    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # HISTÓRICO PERMANENTE
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    # Não existe limpeza de histórico.
    #
    # Cada dia gera um arquivo diferente devido à data no nome.
    #
    # Exemplo:
    #
    # tmp/
    # ├── MB5B_20260831.XLSX
    # ├── MB5B_20260901.XLSX
    # ├── MB5B_20260902.XLSX
    # └── ...
    #
    # Nenhum arquivo antigo é excluído.


    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # VALIDAÇÃO FINAL
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    if erros:

        raise RuntimeError(
            f"Ocorreram erros na extração MB5B: {erros}"
        )

    else:

        print()
        print(
            "=" * 80
        )

        print(
            "PROCESSAMENTO MB5B CONCLUÍDO COM SUCESSO."
        )

        print(
            f"Datas processadas :: {len(datas)}"
        )

        print(
            "=" * 80
        )


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# EXECUÇÃO DIRETA
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

if __name__ == "__main__":

    engdds_mb5b_main()