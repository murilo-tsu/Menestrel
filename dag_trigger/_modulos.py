import os
import shutil

def limpar_pasta(caminho):
    """
    Apaga todos os arquivos e subpastas dentro do caminho informado,
    mantendo a pasta principal.
    """
    if not os.path.exists(caminho):
        print("A pasta não existe.")
        return

    for item in os.listdir(caminho):
        item_path = os.path.join(caminho, item)

        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            print(f"Erro ao apagar {item_path}: {e}")

    print("Pasta limpa com sucesso.")
