import logging
import time
from minio import Minio
from io import BytesIO

class MinioConnector:
    def __init__ (self, host='10.91.5.107:20000', user='datainsights', pswd='Eurochem123#', secure=False):
        
        self.host=host
        self.user=user
        self.pswd=pswd
        self.secure=secure
        self.client=False
        self._pending_uploads=[]

    def _connect(self):

        self.client = Minio(
            self.host,
            access_key=self.user,
            secret_key=self.pswd,
            secure=False
        )

    def _checkConnection(self):
        if not self.client:
            
            try:
                self._connect()
                return True
            except:
                return False
        
        return True
    
    def upload_file(self, local_path, bucket, remote_path):
        try:
            self._checkConnection()
            self.client.fput_object(
                bucket,
                remote_path,
                local_path,
            )
            return True
        except:
            return False
    def upload_from_bytesIO(self, data, bucket, remote_path, max_retries=3, retry_delay=5):
        for attempt in range(1, max_retries + 1):
            try:
                self._checkConnection()
                data.seek(0)
                self.client.put_object(
                    bucket,
                    remote_path,
                    data,
                    data.getbuffer().nbytes
                )
                return True
            except Exception as erro:
                logging.error(f"Falha upload MinIO {bucket}/{remote_path} (tentativa {attempt}/{max_retries}): {erro}")
                if attempt < max_retries:
                    time.sleep(retry_delay)

        return False

    def upload_or_queue(self, data, bucket, remote_path, max_retries=3, retry_delay=5):
        # Falha aqui não interrompe o chamador: enfileira para flush_pending_uploads() tentar depois.
        if self.upload_from_bytesIO(data, bucket, remote_path, max_retries, retry_delay):
            return True

        data.seek(0)
        self._pending_uploads.append((data.read(), bucket, remote_path))
        logging.error(f"Upload de {bucket}/{remote_path} falhou após {max_retries} tentativas; adicionado à fila de reenvio.")
        return False

    def flush_pending_uploads(self, max_rounds=5, retry_delay=30):
        if not self._pending_uploads:
            return True

        for round_num in range(1, max_rounds + 1):
            ainda_pendentes = []
            for content, bucket, remote_path in self._pending_uploads:
                if not self.upload_from_bytesIO(BytesIO(content), bucket, remote_path):
                    ainda_pendentes.append((content, bucket, remote_path))
            self._pending_uploads = ainda_pendentes

            if not self._pending_uploads:
                return True

            logging.error(f"Fila de upload MinIO :: {len(self._pending_uploads)} arquivo(s) ainda pendente(s) após rodada {round_num}/{max_rounds}.")
            if round_num < max_rounds:
                time.sleep(retry_delay)

        for _, bucket, remote_path in self._pending_uploads:
            logging.error(f"Falha definitiva no upload de {bucket}/{remote_path} após {max_rounds} rodadas de reenvio.")
        return False

    def download_file(self, bucket, remote_path, local_path):
        try:
            self._checkConnection()
            self.client.fget_object(
                bucket,
                remote_path,
                local_path,
            )
            return True
        except:
            return False
    
    def download_to_bytesIO(self, bucket, remote_path):
        from io import BytesIO
        try:
            self._checkConnection()
            response = self.client.get_object(
                bucket,
                remote_path,
            )
            data = BytesIO()
            for d in response.stream(32*1024):
                data.write(d)
            data.seek(0)
            return data
        except:
            return False
    
    def list_files(self, bucket, prefix=''):
        try:
            self._checkConnection()
            objects = self.client.list_objects(bucket, prefix=prefix, recursive=True)
            file_list = [obj.object_name for obj in objects if '_SUCCESS' not in obj.object_name]
            return file_list
        except:
            return False
    
    def delete_file(self, bucket, remote_path):
        try:
            self._checkConnection()
            self.client.remove_object(bucket, remote_path)
            return True
        except:
            return False

    def create_bucket(self, bucket):
        try:
            self._checkConnection()
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
            return True
        except:
            return False

    def delete_bucket(self, bucket):
        try:
            self._checkConnection()
            self.client.remove_bucket(bucket)
            return True
        except:
            return False
    
    def list_buckets(self):
        try:
            self._checkConnection()
            buckets = self.client.list_buckets()
            bucket_list = [bucket.name for bucket in buckets]
            return bucket_list
        except:
            return False
    
    def buffer_creator(self, path:str, file:str):
        buffer = BytesIO()
        arquivo = open(path + '/'+ file, 'rb')
        buffer.write(arquivo.read())
        buffer.seek(0)
        return buffer



