import sys
import re
import urllib.parse
import boto3
from datetime import datetime, timedelta
from urllib.parse import urlparse
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.dynamicframe import DynamicFrame
from pyspark.context import SparkContext
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Argumentos recebidos pelo Glue Job
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'input_file'])

# Decodifica a URI
decoded_input_file = urllib.parse.unquote(args['input_file'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

s3 = boto3.client("s3")

# Função para extrair data da key
def extract_date_from_path(path):
    match = re.search(r"anomesdia=(\d{4}-\d{2}-\d{2})", path)
    return match.group(1) if match else None


# Função para pegar último arquivo da partição anterior
def get_last_file_from_partition(s3_path):

    parsed = urlparse(s3_path)
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")

    prefix = "/".join(key.split("/")[:-1]) + "/"

    response = s3.list_objects_v2(
        Bucket=bucket,
        Prefix=prefix
    )

    if "Contents" not in response:
        return None

    files = [obj for obj in response["Contents"] if obj["Key"].endswith(".parquet")]

    if not files:
        return None

    last_file = max(files, key=lambda x: x["LastModified"])

    return f"s3://{bucket}/{last_file['Key']}"


# Extrai data atual
print(decoded_input_file)

current_date_str = extract_date_from_path(decoded_input_file)

if not current_date_str:
    raise ValueError("Data não encontrada no caminho do arquivo.")

current_date = datetime.strptime(current_date_str, "%Y-%m-%d")

# Calcula data anterior
previous_date = current_date - timedelta(days=1)
previous_date_str = previous_date.strftime("%Y-%m-%d")

# Monta caminho da partição anterior
previous_partition = decoded_input_file.replace(current_date_str, previous_date_str)

# Busca último arquivo da partição anterior
previous_file = get_last_file_from_partition(previous_partition)

print(f"Arquivo anterior encontrado: {previous_file}")

# Lê o arquivo atual
df_current = spark.read.parquet(decoded_input_file) \
    .withColumn("anomesdia", F.lit(current_date_str))

# Tenta ler o arquivo anterior
if previous_file:

    df_previous = spark.read.parquet(previous_file) \
        .withColumn("anomesdia", F.lit(previous_date_str))

    df_previous = df_previous \
        .withColumnRenamed("codigo", "ticker") \
        .withColumnRenamed("qtde_teorica", "n_acoes_teoricas")
    print(df_previous)
else:
    print("Aviso: Nenhum arquivo encontrado na partição anterior.")
    df_previous = None


# Renomeia colunas do atual
df_current = df_current \
    .withColumnRenamed("codigo", "ticker") \
    .withColumnRenamed("qtde_teorica", "n_acoes_teoricas")

# Junta datasets
if df_previous:
    df_union = df_current.unionByName(df_previous)
else:
    df_union = df_current

# Define janela
window_spec = Window.partitionBy("ticker", "acao", "tipo").orderBy("anomesdia")

df_union = df_union.withColumn(
    "diff_part_pct",
    F.col("part_pct") - F.lag("part_pct").over(window_spec)
)

# Converte para DynamicFrame
dyf = DynamicFrame.fromDF(df_union, glueContext, "dyf")

# Caminho de saída
output_path = "s3://mlet8-fase2-pos/output_glue/refined/"

# Sink Glue
sink = glueContext.getSink(
    path=output_path,
    connection_type="s3",
    enableUpdateCatalog=True,
    updateBehavior="UPDATE_IN_DATABASE",
    partitionKeys=["anomesdia", "ticker"]
)

sink.setCatalogInfo(
    catalogDatabase="default",
    catalogTableName="acoes_refined"
)

sink.setFormat("glueparquet")

sink.writeFrame(dyf)

print("Dados salvos com sucesso no S3 e catálogo atualizado para Athena.")