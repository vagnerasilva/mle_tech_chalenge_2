import sys
import re
import urllib.parse
from datetime import datetime, timedelta
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.dynamicframe import DynamicFrame
from pyspark.context import SparkContext
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Argumentos recebidos pelo Glue Job
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'input_file'])

# Decodifica a URI para remover %3D
decoded_input_file = urllib.parse.unquote(args['input_file'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Função para extrair data da key
def extract_date_from_path(path):
    match = re.search(r"anomesdia=(\d{4}-\d{2}-\d{2})", path)
    return match.group(1) if match else None

# Extrai data atual
print(decoded_input_file)
current_date_str = extract_date_from_path(decoded_input_file)

if not current_date_str:
    raise ValueError("Data não encontrada no caminho do arquivo.")

current_date = datetime.strptime(current_date_str, "%Y-%m-%d")

# Calcula data anterior
previous_date = current_date - timedelta(days=1)
previous_date_str = previous_date.strftime("%Y-%m-%d")

# Monta caminho do arquivo anterior substituindo a data
previous_file = decoded_input_file.replace(current_date_str, previous_date_str)

# Lê o arquivo atual
df_current = spark.read.parquet(decoded_input_file) \
    .withColumn("anomesdia", F.lit(current_date_str))

# Tenta ler o arquivo anterior (se existir)
try:
    df_previous = spark.read.parquet(previous_file) \
        .withColumn("anomesdia", F.lit(previous_date_str))

    df_previous = df_previous \
        .withColumnRenamed("codigo", "ticker") \
        .withColumnRenamed("qtde_teorica", "n_acoes_teoricas")

except Exception as e:
    print(f"Aviso: Arquivo anterior não encontrado ({previous_file}). Continuando apenas com o atual.")
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

# Define janela para calcular diferença entre períodos
window_spec = Window.partitionBy("ticker", "acao", "tipo").orderBy("anomesdia")

df_union = df_union.withColumn(
    "diff_n_acoes_teoricas",
    F.col("n_acoes_teoricas") - F.lag("n_acoes_teoricas").over(window_spec)
)

# Converte para DynamicFrame
dyf = DynamicFrame.fromDF(df_union, glueContext, "dyf")

# Caminho de saída no S3
output_path = "s3://mlet8-fase2-pos/output_glue/refined/"

# Sink que escreve no S3 e atualiza automaticamente o Glue Catalog
sink = glueContext.getSink(
    path=output_path,
    connection_type="s3",
    enableUpdateCatalog=True,
    updateBehavior="UPDATE_IN_DATABASE",
    partitionKeys=["anomesdia", "ticker"]
)

# Define tabela no Glue Catalog (usada pelo Athena)
sink.setCatalogInfo(
    catalogDatabase="default",
    catalogTableName="acoes_refined"
)

# Formato otimizado para Athena
sink.setFormat("glueparquet")

# Escreve dados
sink.writeFrame(dyf)

print("Dados salvos com sucesso no S3 e catálogo atualizado para Athena.")