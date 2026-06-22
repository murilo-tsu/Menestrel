from minio import Minio
from io import BytesIO

class MinioConnector:
    def __init__ (self, host='10.91.5.107:20000', user='datainsights', pswd='Eurochem123#', secure=False):
        
        self.host=host
        self.user=user
        self.pswd=pswd
        self.secure=secure
        self.client=False

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
    def upload_from_bytesIO(self, data, bucket, remote_path):
        try:
            self._checkConnection()
            self.client.put_object(
                bucket,
                remote_path,
                data,
                data.getbuffer().nbytes
            )

            return True
        except:
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



