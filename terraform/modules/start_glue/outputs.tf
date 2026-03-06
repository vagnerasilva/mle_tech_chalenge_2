output "glue_job_name" {
  value = aws_glue_job.this.name
}

output "glue_trigger_name" {
  value = aws_glue_trigger.daily.name
}
