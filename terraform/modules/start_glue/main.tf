resource "aws_iam_role" "glue_role" {
  name = "${var.job_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Principal = { Service = "glue.amazonaws.com" },
      Effect = "Allow"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "glue_policy_attach" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_glue_job" "this" {
  name     = var.job_name
  role_arn = aws_iam_role.glue_role.arn

  command {
    name            = "glueetl"
    script_location = var.script_path
    python_version  = "3"
  }

  default_arguments = {
    "--job-language" = "python"
    "--TempDir"      = "${var.output_path}/tmp/"
    "--enable-metrics" = "true"
  }

  max_capacity = 2
}

resource "aws_glue_trigger" "daily" {
  name     = "${var.job_name}-trigger"
  type     = "SCHEDULED"
  schedule = var.schedule_cron

  actions {
    job_name = aws_glue_job.this.name
  }
}
