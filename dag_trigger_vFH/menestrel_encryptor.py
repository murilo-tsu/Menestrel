import cryptocode
import random
import os

_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%&*()-_=+'

class sap_crypto():
    
    def __init__(self):
        self.key = ''.join([_chars[random.randint(0, len(_chars) - 1)] for _ in range(len(_chars))])

    def criar_arquivo_criptografado(self, user, password, path=None):
        if path is None:
            # Usa o diretório onde está este script
            path = os.path.dirname(os.path.abspath(__file__))
        
        enc_user = cryptocode.encrypt(user, self.key)
        enc_pass = cryptocode.encrypt(password, self.key)

        # Escreve uma chave aleatória para criptografia
        with open(os.path.join(path,'key.key'), 'w') as _key:
            _key.write(self.key)

        # Escreve usuário criptografado
        with open(os.path.join(path,'user.enc'), 'w') as _userfile:
            _userfile.write(enc_user)
        
        # Escreve senha criptografada
        with open(os.path.join(path,'senha.enc'), 'w') as _passfile:
            _passfile.write(enc_pass)
        
        print(f"Arquivos criados em: {path}")
    
    def obter_credencias(self, path=None):
        if path is None:
            # Usa o diretório onde está este script
            path = os.path.dirname(os.path.abspath(__file__))
        
        # Verifica se os arquivos existem
        key_path = os.path.join(path, 'key.key')
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"Arquivo {key_path} não encontrado. Execute criar_arquivo_criptografado primeiro.")
        
        # Lê uma chave aleatória previamente gerada
        with open(key_path, 'r') as _key_read:
            existing_key = _key_read.read()
        
        # Lê um usuário previamente criptografado
        user_path = os.path.join(path, 'user.enc')
        with open(user_path, 'r') as _userfile_read:
            _user = _userfile_read.read()
        dec_user = cryptocode.decrypt(_user, existing_key)

        # Lê uma senha previamente criptografada
        pass_path = os.path.join(path, 'senha.enc')
        with open(pass_path, 'r') as _passfile_read:
            _pass = _passfile_read.read()
        dec_password = cryptocode.decrypt(_pass, existing_key)

        return dec_user, dec_password

class sp_crypto():
    def __init__(self):
        self.key = ''.join([_chars[random.randint(0, len(_chars) - 1)] for _ in range(len(_chars))])
    
    def credenciais_sharepoint(self, path=None):
        if path is None:
            # Usa o diretório onde está este script
            path = os.path.dirname(os.path.abspath(__file__))
        
        # Verifica se os arquivos existem
        sp_key_path = os.path.join(path, 'sp_key.key')
        if not os.path.exists(sp_key_path):
            raise FileNotFoundError(f"Arquivo {sp_key_path} não encontrado.")
        
        # Ler a chave gerada para acessar o sharepoint
        with open(sp_key_path, 'r') as _sp_key_read:
            sp_existing_key = _sp_key_read.read()
        
        # Ler usuário do SharePoint
        sp_user_path = os.path.join(path, 'sp_user.enc')
        with open(sp_user_path, 'r') as _sp_userfiled_read:
            _sp_user = _sp_userfiled_read.read()
        dec_sp_user = cryptocode.decrypt(_sp_user, sp_existing_key)

        # Ler senha do SharePoint
        sp_pass_path = os.path.join(path, 'sp_pass.enc')
        with open(sp_pass_path, 'r') as _sp_passfile_read:
            _sp_pass = _sp_passfile_read.read()
        dec_sp_password = cryptocode.decrypt(_sp_pass, sp_existing_key)

        return dec_sp_user, dec_sp_password

if __name__ == "__main__":
    # Garante que estamos no diretório correto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Diretório do script: {script_dir}")
    
    sap_crypto().criar_arquivo_criptografado(
        user=input('Informar usuário: '),
        password=input('Informar senha: ')
    )