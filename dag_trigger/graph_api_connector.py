import msal, requests
import time
from dateutil.parser import isoparse
import os
import json
from io import BytesIO
import pandas as pd
from urllib.parse import quote, unquote
class sharepoint:
    def __init__(self,client_id, client_secret, psharepoint='https://fertilizantes.sharepoint.com/sites/DataInsight/', tenant_id="ded15a52-cfc6-4bda-975c-54f6eae2403e",change_lib = False):
        '''
            :param client_id: ID do cliente registrado no Azure AD
            :param client_secret: Segredo do cliente registrado no Azure AD
            :param psharepoint: URL do site SharePoint
            :param tenant_id: ID do locatário do Azure AD
            :param change_lib: Indica se a biblioteca padrão deve ser alterada
        '''
        
        
        self.client_id = client_id
        self.secret_id = client_secret
        self.tenant_id = tenant_id
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]
        self.token = ''
        self.headers = ''
        self.psharepoint = psharepoint
        self.site_id = ''
        self.drive_id = ''
        self.change_lib = change_lib

    def connect(self):
        '''
            Função para conexão na GraphAPI.
            Atualiza o token, header, site_id e drive_id dentro do objeto.
            Esses parâmetros são usados em todas as requisições futuras dentro dos outros métodos
        '''
        
        app = msal.ConfidentialClientApplication(
            self.client_id, authority=self.authority,
            client_credential=self.secret_id
        )
        self.token = app.acquire_token_for_client(scopes=self.scope)['access_token']
        self.headers = {"Authorization": f"Bearer {self.token}"}

        self.psharepoint = self.psharepoint.replace('https://','')

        self.psharepoint = self.psharepoint.split('/')
        self.psharepoint[0] = self.psharepoint[0]+':'
        self.psharepoint = '/'.join(self.psharepoint)

        resp = requests.get(
            f"https://graph.microsoft.com/v1.0/sites/{self.psharepoint}?$select=id,name,webUrl",
            headers=self.headers
        )

        resp.raise_for_status()
        self.site_id=resp.json()['id']
        if self.change_lib:
            resp = requests.get(f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives", headers=self.headers)
            values = resp.json()['value']
            self.drive_id = [value['id'] for value in values if self.change_lib in unquote(value['webUrl'])][0]
        else:
            resp = requests.get(f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drive", headers=self.headers)
            resp.raise_for_status()
            self.drive_id = resp.json()['id']
        return True

    def criar_upload_session(self, remote_path):
        
        remote_path = '/'.join(remote_path.split('/')[1:])
        
        url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/root:/{remote_path}:/createUploadSession"
        payload = {
            "item": {
                "@microsoft.graph.conflictBehavior": 'replace',
                
            }
        }
        resp = requests.post(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["uploadUrl"], data.get("expirationDateTime")
    
    def enviar_chunk(self, sess: requests.Session, upload_url: str, chunk: bytes, start: int, end: int, total: int) -> requests.Response:
        """
        Envia um único chunk com Content-Range.
        """
        headers = {
            "Content-Length": str(end - start + 1),
            "Content-Range": f"bytes {start}-{end}/{total}",
        }
        return sess.put(upload_url, headers=headers, data=chunk)

    def upload(self, remote_path: str, local_path: str, size_chunk: int = 10000000,retries=5):
        drive_path = remote_path
        arquivo_local = local_path
        chunk_size = size_chunk
        if self.token == '':
            self.connect()
        if not drive_path.endswith('/'):
            drive_path +='/'
        

        upload_url, exp_iso = self.criar_upload_session(drive_path+arquivo_local.split('/')[-1])
        total = os.path.getsize(arquivo_local)
        
        sess = requests.Session()
        enviados = 0
        tentativa = 0
        max_tentativas = retries  # ~1+2+4+8+16+20s de backoff

        with open(arquivo_local, "rb") as f:
            while enviados < total:
                # Calcula intervalo do próximo chunk
                start = enviados
                end = min(start + chunk_size - 1, total - 1)
                f.seek(start)
                chunk = f.read(end - start + 1)

                tentativa = 0
                while True:
                    tentativa += 1
                    try:
                        resp = self.enviar_chunk(sess, upload_url, chunk, start, end, total)
                        # 202 = ainda faltam bytes; 201/200 = finalizado; 2xx em geral OK
                        if resp.status_code in (200, 201):
                            # Upload finalizado
                            print("Upload concluído com sucesso.")
                            return

                        if resp.status_code == 202:
                            # Parcialmente enviado. Graph pode retornar nextExpectedRanges.
                            enviados = end + 1
                            # Barra de progresso simples
                            pct = (enviados / total) * 100
                            print(f"\rEnviado: {enviados:,}/{total:,} bytes ({pct:.2f}%)", end="")
                            break  # sair do loop de retry e ir para o próximo chunk

                        # Erros recuperáveis: 5xx e 429 (throttling)
                        if resp.status_code in (429, 500, 502, 503, 504):
                            if tentativa >= max_tentativas:
                                resp.raise_for_status()
                            retry_after = resp.headers.get("Retry-After")
                            if retry_after:
                                time.sleep(float(retry_after))
                            else:
                                self.backoff_sleep(tentativa)
                            continue

                        # Outros erros => exceção
                        resp.raise_for_status()

                    except requests.RequestException as e:
                        if tentativa >= max_tentativas:
                            raise
                        self.backoff_sleep(tentativa)
                        continue

        # Se saiu do loop sem 200/201, algo deu errado
        raise RuntimeError("Upload não foi finalizado corretamente (sem status 200/201).")
