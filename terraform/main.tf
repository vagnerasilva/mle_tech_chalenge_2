module "glue_job" {
  source        = "./modules/glue_job"
  job_name      = var.job_name
  script_path   = var.script_path
  output_path   = var.output_path
  schedule_cron = var.schedule_cron
}
