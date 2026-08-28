from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
from minio import Minio
from minio.error import S3Error
from minio.commonconfig import CopySource
from _modules.rabbitMQ import RabbitMQ
from datetime import datetime
import pandas as pd
from io import BytesIO
import os
import zipfile


class Spark:
    def __init__(self, app_name,
                 minio_user='datainsights_fh',
                 minio_pass='Heringer123',
                 minio_host='10.91.5.108:9000'):

        jars = ",".join([
            "/python_scripts/_modules/spark_addons/hadoop_336/hadoop-common-3.3.6.jar",
            "/python_scripts/_modules/spark_addons/hadoop_336/hadoop-auth-3.3.6.jar",
            "/python_scripts/_modules/spark_addons/hadoop_336/hadoop-hdfs-client-3.3.6.jar",
            "/python_scripts/_modules/spark_addons/hadoop_336/hadoop-client-api-3.3.6.jar",
            "/python_scripts/_modules/spark_addons/hadoop_336/hadoop-client-runtime-3.3.6.jar",
            "/python_scripts/_modules/spark_addons/hadoop_336/hadoop-aws-3.3.6.jar",
            "/python_scripts/_modules/spark_addons/hadoop_336/aws-java-sdk-bundle-1.12.762.jar",

            # PARQUET 1.13.1 (versão correta)
            "/python_scripts/_modules/spark_addons/parquet/parquet-hadoop-1.13.1.jar",
            "/python_scripts/_modules/spark_addons/parquet/parquet-common-1.13.1.jar",
            "/python_scripts/_modules/spark_addons/parquet/parquet-column-1.13.1.jar",
            "/python_scripts/_modules/spark_addons/parquet/parquet-encoding-1.13.1.jar",
            "/python_scripts/_modules/spark_addons/parquet/parquet-jackson-1.13.1.jar",
            "/python_scripts/_modules/spark_addons/parquet/parquet-format-2.9.0.jar",
        ])



        extra_log_opts = (
            "-Dlog4j.rootCategory=ERROR,console "
            "-Dlog4j.logger.org.apache.spark=ERROR "
            "-Dlog4j.logger.org.apache.hadoop=ERROR "
        )

        self.spark = (
            SparkSession.builder
            .appName(app_name)
            .config("spark.jars", jars)
            .config("spark.driver.extraClassPath", jars)
            .config("spark.executor.extraClassPath", jars)

            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
            .config("spark.hadoop.fs.s3a.aws.credentials.provider",
                    "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")

            .config("spark.hadoop.fs.s3a.endpoint", f"http://{minio_host}")
            .config("spark.hadoop.fs.s3a.access.key", minio_user)
            .config("spark.hadoop.fs.s3a.secret.key", minio_pass)

            .config("spark.hadoop.fs.s3a.path.style.access", "true")
            .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")

            # Melhorias para evitar erros ao ler Parquet:
            .config("spark.hadoop.fs.s3a.connection.timeout", "600000")
            .config("spark.hadoop.fs.s3a.socket.timeout", "600000")




            # EXEC LOCAL
            .config("spark.master", "local[2]")
            .config("spark.driver.memory", "8g")
            .config("spark.executor.memory", "2g")
            .config("spark.executor.cores", "1")

            .getOrCreate()
        )

        self.spark.sparkContext.setLogLevel("ERROR")

        # CLIENTE DO MINIO PARA OPERAÇÕES DIRETAS
        self.minio_client = Minio(
            minio_host,
            access_key=minio_user,
            secret_key=minio_pass,
            secure=False
        )


    def write_to_minio(self, df, bucket, key, format="parquet", mode="overwrite", **options):
        """
        Grava o DataFrame `df` no MinIO em s3a://{bucket}/{key}.

        :param df: DataFrame do PySpark a ser gravado.
        :param bucket: nome do bucket no MinIO.
        :param key: caminho/chave dentro do bucket (pode terminar em pasta ou incluir nome de arquivo).
        :param format: "parquet", "csv", "json", "orc", etc.
        :param mode: modo de gravação ("overwrite", "append", "errorifexists", "ignore").
        :param options: outras opções de escrita (por ex. sep para CSV).
        """
        try:
            path = f"s3a://{bucket}/{key}"
            writer = (
                df.write
                .mode(mode)
                .format(format)
            )

            # aplica opções extras, se houver
            for k, v in options.items():
                writer = writer.option(k, v)

            writer.save(path)
        except Exception as erro:
            print(erro)
            pass
        
        # Instanciar a mensageria do RabbitMQ declarada em rabbitmq.py
        # Ao executar um procedimento de gravação, publica-se uma mensagem na fila deleta_temp
        rabbit = RabbitMQ()
        rabbit.publicar_mensagem('remover_pasta_temp_107', str({"bucket":f"{bucket}", "folder":f"{key}"}).replace("'",'"'))
    
    # 2025-11-10 -- Método de Gravação por partição
    # Motivo: Na leitura de bancos com volume alto de linhas, cada processamento de pastas isoladas requer uma
    # nova consulta spark, que por definição opera melhor quando não precisa materializar com frequência os dados
    def partitioned_write_to_minio(self, df, bucket, key, format="parquet", mode="overwrite", folder=None, **options):
        """
        Grava o DataFrame `df` no MinIO em s3a://{bucket}/{key}/{folder}.
        
        O >> folder << indica uma partição possível para os parquets, otimizando a gravação
        em paralelo sem perder a facilidade de quebra em pastas.

        :param df: DataFrame do PySpark a ser gravado.
        :param bucket: nome do bucket no MinIO.
        :param key: caminho/chave dentro do bucket (pode terminar em pasta ou incluir nome de arquivo).
        :param format: "parquet", "csv", "json", "orc", etc.
        :param mode: modo de gravação ("overwrite", "append", "errorifexists", "ignore").
        :param partitionBy: partição selecionada para quebra dos parquets.
        :param options: outras opções de escrita (por ex. sep para CSV).
        """   
        
        try:    
            path = f"s3a://{bucket}/{key}"
            writer = df.write.mode(mode).format(format)
            if folder is not None:
                if isinstance(folder, str):
                    writer = writer.partitionBy(folder)
                else:
                    writer = writer.partitionBy(*folder)
            for k,v in options.items():
                writer = writer.option(k, v)
            
            writer.save(path)
        except Exception as erro:
            print(erro)
            pass

        # Instanciar a mensageria do RabbitMQ declarada em rabbitmq.py
        # Ao executar um procedimento de gravação, publica-se uma mensagem na fila deleta_temp        
        rabbit = RabbitMQ()
        rabbit.publicar_mensagem('remover_pasta_temp_107', str({"bucket":f"{bucket}", "folder":f"{key}"}).replace("'",'"'))
    
    def read_from_minio(self, bucket: str, key: str, format: str = "parquet", **options):
        """
        Lê dados do MinIO (via s3a) e retorna um DataFrame.
        :param bucket: nome do bucket no MinIO.
        :param key: caminho/chave dentro do bucket (pode ser diretório ou arquivo).
        :param format: formato dos dados ("parquet", "csv", "json", "orc", etc.).
        :param options: opções específicas de leitura (por ex. header, sep, inferSchema para CSV).
        """
        path = f"s3a://{bucket}/{key}"
        reader = self.spark.read.format(format)
        for opt_name, opt_val in options.items():
            reader = reader.option(opt_name, opt_val)
        return reader.load(path)


    def read_parquet_local(self, path):
        return self.spark.read.parquet('file://' + path)
    def write_parquet(self, df, path, mode='overwrite'):
        df.write.parquet(f"{self.hdfs_host}/{path}", mode=mode)
    def read_parquet(self, path):
        return self.spark.read.parquet(f"{self.hdfs_host}/{path}")
    def sql(self, query,com_type='string'):
        if com_type == 'file':
            arq_com = open(query, 'r', encoding='UTF-8')

            sql_com = ''
            for line in arq_com.readlines():
                sql_com+=line

            query = sql_com
        return self.spark.sql(query)
    def list_hdfs_files(self, path):
        """Lista arquivos em um diretório HDFS e retorna uma lista de nomes de arquivos"""
        try:
            file_list = self.hdfs_client.list(path)
            return file_list
        except Exception as e:
            return [f"Erro ao listar arquivos no HDFS: {str(e)}"]
    def delete_hdfs_path(self, path):
        """Deleta um arquivo ou diretório no HDFS"""
        try:
            self.hdfs_client.delete(path, recursive=True)
            return f"Caminho {path} deletado com sucesso."
        except Exception as e:
            return f"Erro ao deletar caminho no HDFS: {str(e)}"
    def concat(self,dfs):
        """
        Concatena uma lista de DataFrames do PySpark.
        """
        if not dfs:
            return None
        df = dfs[0]

        for i in range(1, len(dfs)):
            colsa = set(df.columns)
            colsb = set(dfs[i].columns)
            create_b = [col for col in colsa if col not in colsb]
            create_a = [col for col in colsb if col not in colsa]
            for col in create_b:
                dfs[i] = dfs[i].withColumn(col, lit(None))
            for col in create_a:
                df = df.withColumn(col, lit(None))
            df = df.union(dfs[i])
        return df

    def rename_cols(self, df, cols):

        """
        Renomeia as colunas de um DataFrame do PySpark.
        """
        for col in cols.keys():
            df = df.withColumnRenamed(col, cols[col])
        return df
    
    def stop(self):
        self.spark.stop()

    def spark_log_execution(self, camada: str, table: str):
        df = self.spark.createDataFrame(
            [(camada, table)],
            ["camada", "table"])
        return self.write_to_minio(df, 'stage', f'log_execution/', mode="append")

    # 2025-10-27 :: Alteração de método para incluir padrões de partição
    def delete_folder(self, bucket: str, prefix: str, part: str = None):
        """
        Deleta todos os objetos dentro de um "folder" (prefixo) no MinIO.
        :param bucket: nome do bucket.
        :param prefix: prefixo dos objetos (ex: "folder1/subfolder2/").
        :param part: partição de dados em uma pasta específica
        """
        try:
            minio_client = Minio(
                endpoint=self.spark.sparkContext._jsc.hadoopConfiguration().get("fs.s3a.endpoint").replace("http://", "").replace("https://", ""),
                access_key=self.spark.sparkContext._jsc.hadoopConfiguration().get("fs.s3a.access.key"),
                secret_key=self.spark.sparkContext._jsc.hadoopConfiguration().get("fs.s3a.secret.key"),
                secure=False
            )

            clean_prefix = prefix.lstrip('/')
            objects_to_delete = minio_client.list_objects(bucket, prefix=clean_prefix, recursive=True)
            deleted = 0
            for obj in objects_to_delete:
                if part is None or part in obj.object_name:
                    print(f"Deletando: {obj.object_name}")
                    minio_client.remove_object(bucket, obj.object_name)
                    deleted += 1
                    

            return f"Total de objetos deletados em '{prefix}': {deleted}"

        except S3Error as e:
            return f"Erro ao deletar objetos no MinIO: {str(e)}"
        except Exception as ex:
            return f"Erro inesperado: {str(ex)}"

    def _delete_all_folders(self, bucket: str, exclude_prefixes: list[str] = None):
        """
        Deleta todos os objetos dentro de um bucket no MinIO, exceto os que estão nas pastas especificadas.

        :param bucket: nome do bucket.
        :param exclude_prefixes: lista de prefixos (pastas) que não devem ser deletados.
        """
        exclude_prefixes = exclude_prefixes or []

        try:
            minio_client = Minio(
                endpoint=self.spark.sparkContext._jsc.hadoopConfiguration().get("fs.s3a.endpoint").replace("http://", "").replace("https://", ""),
                access_key=self.spark.sparkContext._jsc.hadoopConfiguration().get("fs.s3a.access.key"),
                secret_key=self.spark.sparkContext._jsc.hadoopConfiguration().get("fs.s3a.secret.key"),
                secure=False
            )

            objects_to_delete = minio_client.list_objects(bucket, recursive=True)
            deleted = 0

            for obj in objects_to_delete:
                # Verifica se o objeto começa com algum dos prefixos a serem ignorados
                if any(obj.object_name.startswith(prefix) for prefix in exclude_prefixes):
                    print(f"Pulando (excluído da exclusão): {obj.object_name}")
                    continue

                print(f"Deletando: {obj.object_name}")
                minio_client.remove_object(bucket, obj.object_name)
                deleted += 1

            return f"Total de objetos deletados no bucket '{bucket}': {deleted}"

        except S3Error as e:
            return f"Erro ao deletar objetos no MinIO: {str(e)}"
        except Exception as ex:
            return f"Erro inesperado: {str(ex)}"
    
    def snapshot_buckets(self, source_buckets: list[str], snapshot_bucket: str):
            """
            Cria um 'snapshot' de buckets selecionados, copiando todos os objetos para um bucket de backup.

            :param source_buckets: Lista de buckets a serem copiados.
            :param snapshot_bucket: Nome do bucket onde o snapshot será armazenado.
            :param snapshot_prefix: Prefixo (pasta) dentro do snapshot_bucket para organização dos snapshots.
            """
            try:
                minio_client = Minio(
                    endpoint=self.spark.sparkContext._jsc.hadoopConfiguration().get("fs.s3a.endpoint").replace("http://", "").replace("https://", ""),
                    access_key=self.spark.sparkContext._jsc.hadoopConfiguration().get("fs.s3a.access.key"),
                    secret_key=self.spark.sparkContext._jsc.hadoopConfiguration().get("fs.s3a.secret.key"),
                    secure=False
                )

                timestamp = timestamp = datetime.utcnow().strftime("%Y_%m_%d")
                total_copied = 0

                for bucket in source_buckets:
                    print(f"\nCopiando bucket: {bucket}")

                    objects = minio_client.list_objects(bucket, recursive=True)
                    for obj in objects:
                        source_path = obj.object_name

                        dest_object_name = f"{timestamp}/{bucket}/{source_path}"

                        # Copia o objeto para o bucket de snapshot
                        minio_client.copy_object(
                            bucket_name=snapshot_bucket,
                            object_name=dest_object_name,
                            source = CopySource(bucket, source_path)
                        )
                        total_copied += 1
                        print(f"Copiado: {bucket}/{source_path} ➜ {snapshot_bucket}/{dest_object_name}")

                return f"Snapshot concluído. Total de objetos copiados: {total_copied}"

            except S3Error as e:
                return f"Erro ao criar snapshot: {str(e)}"
            except Exception as ex:
                return f"Erro inesperado: {str(ex)}"
            
    
    def list_minio_metadata(self, bucket: str, prefix: str = "", recursive: bool = True):
        """
        Lista recursivamente todos os objetos em um bucket/prefixo no MinIO 
        e retorna os metadados em um DataFrame Spark.

        :param bucket: nome do bucket no MinIO.
        :param prefix: chave inicial (pode ser "" para raiz).
        :param recursive: se True, percorre recursivamente subdiretórios.
        :return: DataFrame Spark com metadados dos arquivos.
        """
        try:
            jvm = self.spark._jvm
            hadoop_conf = self.spark._jsc.hadoopConfiguration()

            base_path = f"s3a://{bucket}/{prefix}"
            jpath = jvm.org.apache.hadoop.fs.Path(base_path)
            fs = jpath.getFileSystem(hadoop_conf)

            def _collect_status(path):
                """Coleta metadados recursivamente, ignorando pastas inexistentes ou inacessíveis."""
                result = []
                try:
                    statuses = fs.listStatus(path)
                except Exception:
                    # Se não consegue listar (pasta não existe ou sem permissão), ignora
                    return result

                for status in statuses:
                    if status.isDirectory() and recursive:
                        result.extend(_collect_status(status.getPath()))
                    else:
                        result.append({
                            "path": str(status.getPath().toString()),
                            "length": status.getLen(),
                            "modification_time": status.getModificationTime(),
                            "owner": status.getOwner(),
                            "group": status.getGroup(),
                            "replication": status.getReplication(),
                            "block_size": status.getBlockSize(),
                            "is_directory": status.isDirectory(),
                            "permission": str(status.getPermission())
                        })
                return result

            metadata_list = _collect_status(jpath)

            if not metadata_list:
                # Se não encontrou nada, retorna DataFrame vazio com schema definido
                return self.spark.createDataFrame([], schema="""
                    path STRING, length BIGINT, modification_time BIGINT,
                    owner STRING, group STRING, replication INT,
                    block_size BIGINT, is_directory BOOLEAN, permission STRING
                """)

            return self.spark.createDataFrame(metadata_list)

        except Exception as e:
            # Se houve erro inesperado, retorna DataFrame com erro
            return self.spark.createDataFrame([{"error": str(e)}])

    def list_minio_folders(self, bucket: str, prefix: str = "", recursive: bool = False):
        """
        Lista todas as 'pastas' (prefixos) de um bucket no MinIO.

        :param bucket: Nome do bucket no MinIO.
        :param prefix: Prefixo inicial (ex: "raw/"). Default = "" (raiz do bucket).
        :param recursive: Se True, lista pastas de forma recursiva.
        :return: Lista de pastas únicas.
        """
        try:
            # Inicializa cliente MinIO usando as configs do Spark
            minio_client = Minio(
                endpoint=self.spark.sparkContext._jsc.hadoopConfiguration().get("fs.s3a.endpoint").replace("http://", "").replace("https://", ""),
                access_key=self.spark.sparkContext._jsc.hadoopConfiguration().get("fs.s3a.access.key"),
                secret_key=self.spark.sparkContext._jsc.hadoopConfiguration().get("fs.s3a.secret.key"),
                secure=False
            )

            objects = minio_client.list_objects(bucket, prefix=prefix, recursive=recursive)

            folders = set()
            for obj in objects:
                parts = obj.object_name.split("/")
                if len(parts) > 1:
                    # Se o objeto pertence a uma pasta, guarda a primeira parte do caminho
                    if prefix:
                        folder = "/".join(parts[:len(prefix.split("/"))+1])
                    else:
                        folder = parts[0]
                    folders.add(folder + "/")

            return sorted(folders)

        except S3Error as e:
            return [f"Erro ao listar pastas no MinIO: {str(e)}"]
        except Exception as ex:
            return [f"Erro inesperado: {str(ex)}"]
        

    def download_and_zip_bucket(self, bucket: str, local_dir: str, zip_path: str, prefix: str = ""):
        """
        Baixa todas as pastas/objetos de um bucket do MinIO para a VM e compacta em .zip.

        :param bucket: Nome do bucket no MinIO
        :param local_dir: Diretório local temporário para salvar os arquivos
        :param zip_path: Caminho final do arquivo .zip
        :param prefix: (opcional) prefixo/pasta dentro do bucket
        """
        try:
            # Inicializa cliente MinIO com configs do Spark
            minio_client = Minio(
                endpoint=self.spark.sparkContext._jsc.hadoopConfiguration().get("fs.s3a.endpoint")
                    .replace("http://", "").replace("https://", ""),
                access_key=self.spark.sparkContext._jsc.hadoopConfiguration().get("fs.s3a.access.key"),
                secret_key=self.spark.sparkContext._jsc.hadoopConfiguration().get("fs.s3a.secret.key"),
                secure=False
            )

            # Criar diretório local se não existir
            os.makedirs(local_dir, exist_ok=True)

            # Listar objetos do bucket
            objects = minio_client.list_objects(bucket, prefix=prefix, recursive=True)

            # Baixar cada objeto para local_dir
            for obj in objects:
                local_path = os.path.join(local_dir, obj.object_name)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                minio_client.fget_object(bucket, obj.object_name, local_path)
                print(f"Baixado: {obj.object_name} → {local_path}")

            # Compactar em ZIP
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(local_dir):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, local_dir)  # manter estrutura de pastas
                        zipf.write(full_path, rel_path)

            return f"✅ Backup concluído. Arquivo gerado: {zip_path}"

        except S3Error as e:
            return f"Erro MinIO: {str(e)}"
        except Exception as ex:
            return f"Erro inesperado: {str(ex)}"


class PdMinio():
    def __init__(self, user='datainsights_fh', password='Heringer123', host='10.91.5.108:9000', **kwargs):
        self.user = user
        self.password = password
        self.host = host

        # Configurações do MinIO
        self.minio_client = Minio(self.host,
                            access_key=self.user,
                            secret_key=self.password,
                            secure=False)  # Se estiver usando HTTPS, altere para True

    def pd_read_files(self,bucket, path, recursive=True):

        if path[-1] != '/' : path+='/'

        # Listar objetos Parquet no MinIO com o prefixo dado
        objects = [f for f in self.minio_client.list_objects(bucket, path,recursive=recursive) if '_SUCCESS' not in f.object_name]

        # Lista para armazenar os DataFrames de cada parte
        dfs = []

        # Iterar sobre os objetos e ler cada parte do Parquet
        for obj in objects:
            # Baixar o objeto do MinIO
            parquet_data = self.minio_client.get_object(bucket, obj.object_name)
            parquet_data = parquet_data.read()

            # Carregar o arquivo Parquet usando o Pandas
            df_part = pd.read_parquet(BytesIO(parquet_data))

            # Adicionar o DataFrame da parte à lista
            dfs.append(df_part)

        # Concatenar todos os DataFrames em um único DataFrame final
        df_final = pd.concat(dfs, ignore_index=True)

        return df_final
