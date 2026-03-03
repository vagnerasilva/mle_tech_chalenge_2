import sys
import re
from datetime import datetime, timedelta
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.dynamicframe import DynamicFrame
from pyspark.context import SparkContext
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Argumentos recebidos pelo Glue Job
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'input_file', 'output_path'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Função para extrair data da key
def extract_date_from_path(path):
    match = re.search(r"anomesdia=(\d{4}-\d{2}-\d{2})", path)
    return match.group(1) if match else None

# Extrai data atual
current_date_str = extract_date_from_path(args['input_file'])
current_date = datetime.strptime(current_date_str, "%Y-%m-%d")

# Calcula data anterior
previous_date = current_date - timedelta(days=1)
previous_date_str = previous_date.strftime("%Y-%m-%d")

# Monta caminho do arquivo anterior substituindo a data
previous_file = args['input_file'].replace(current_date_str, previous_date_str)

# Lê os dois arquivos
df_current = spark.read.parquet(args['input_file']).withColumn("anomesdia", F.lit(current_date_str))
df_previous = spark.read.parquet(previous_file).withColumn("anomesdia", F.lit(previous_date_str))

# Renomeia colunas
df_current = df_current.withColumnRenamed("codigo", "ticker").withColumnRenamed("qtde_teorica", "n_acoes_teoricas")
df_previous = df_previous.withColumnRenamed("codigo", "ticker").withColumnRenamed("qtde_teorica", "n_acoes_teoricas")

# Junta os dois datasets
df_union = df_current.unionByName(df_previous)

# Define janela para calcular diferença entre períodos
window_spec = Window.partitionBy("ticker", "acao", "tipo").orderBy("anomesdia")

df_union = df_union.withColumn(
    "diff_n_acoes_teoricas",
    F.col("n_acoes_teoricas") - F.lag("n_acoes_teoricas").over(window_spec)
)

# Converte para DynamicFrame
dyf = DynamicFrame.fromDF(df_union, glueContext, "dyf")

# Salva em formato Parquet, particionado por data e ticker
glueContext.write_dynamic_frame.from_options(
    frame=dyf,
    connection_type="s3",
    connection_options={
        "path": args['output_path'] + "/refined/",
        "partitionKeys": ["anomesdia", "ticker"]
    },
    format="parquet"
)

# Atualiza metadados no Glue Catalog
glueContext.write_dynamic_frame.from_catalog(
    frame=dyf,
    database="default",
    table_name="acoes_refined"
)
