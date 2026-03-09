import boto3
import json

glue_client = boto3.client("glue")

def lambda_handler(event, context):
    """
    Função Lambda disparada por evento do S3.
    Envia o nome do arquivo que disparou a Lambda como argumento para um Glue Job.
    """
    try:
        # Extrai informações do arquivo do evento S3
        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        print(f"Arquivo recebido: s3://{bucket}/{key}")

        # Nome do Glue Job
        job_name = "glue_refined_spark" 
        print(job_name)
        # Passa o caminho do arquivo como argumento para o Glue Job
        args = {
            "--input_file": f"s3://{bucket}/{key}"
        }
        print('args: ', args)
        response = glue_client.start_job_run(
            JobName=job_name,
            Arguments=args
        )

        job_run_id = response["JobRunId"]
        print({
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Glue Job '{job_name}' iniciado",
                "JobRunId": job_run_id,
                "input_file": f"s3://{bucket}/{key}"
            })
        })
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Glue Job '{job_name}' iniciado",
                "JobRunId": job_run_id,
                "input_file": f"s3://{bucket}/{key}"
            })
        }

    except Exception as e:
        print({
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        })
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }