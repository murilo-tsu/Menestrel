import cryptocode
import random
import os

_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%&*()-_=+'

class sap_crypto():
    
    def __init__(self):
        self.key = ''.join([_chars[random.randint(0, len(_chars) - 1)] for _ in range(len(_chars))])

    def criar_arquivo_criptografado(self, user, password, path = os.getcwd()):
        enc_user = cryptocode.encrypt(user, self.key)
        enc_pass = cryptocode.encrypt(password, self.key)

        # Escreve uma chave aleatória para criptografia
        with open(os.path.join(path,'key.key'), 'w') as _key:
            _key.write(self.key)

        # Escreve uma chave aleatória para criptografar o >> USUÁRIO <<
        with open(os.path.join(path,'user.enc'), 'w') as _userfile:
            _userfile.write(enc_user)
        
        # Escreve uma chave aleatório para criptografar a >> SENHA <<
        with open(os.path.join(path,'senha.enc'), 'w') as _passfile:
            _passfile.write(enc_pass)
        
    
    def obter_credencias(self, path = os.getcwd()):
        
        # Lê uma chave aleatória previamente gerada
        with open(os.path.join(path,'key.key'), 'r') as _key_read:
            existing_key = _key_read.read()
        
        # Lê um usuário previamente criptografado
        with open(os.path.join(path,'user.enc'), 'r') as _userfile_read:
            _user = _userfile_read.read()
        dec_user = cryptocode.decrypt(_user, existing_key)

        # Lê uma senha previamente criptografada
        with open(os.path.join(path,'senha.enc'), 'r') as _passfile_read:
            _pass = _passfile_read.read()
        dec_password = cryptocode.decrypt(_pass, existing_key)

        return dec_user, dec_password

if __name__ == "__main__":
    sap_crypto().criar_arquivo_criptografado(user = input('Informar usuário: '),
                                             password = input('Informar senha: '))
    