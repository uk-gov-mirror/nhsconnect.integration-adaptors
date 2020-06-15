
# Common setting for entire Env - "base" component
environment = "build2"
base_cidr_block = "10.15.0.0/16"
cluster_container_insights = "disabled"
docdb_instance_class = "db.r5.large"
docdb_master_user = "master-user"
docdb_master_password = "ChangeMe" # Here only for the time of development, destroy the db before merge

# Settings for "nhais" component
nhais_service_minimal_count = 1
nhais_service_desired_count = 2
nhais_service_maximal_count = 4
nhais_service_target_request_count = 1200
nhais_service_container_port = 8080
nhais_service_launch_type = "FARGATE"
nhais_log_level = "DEBUG"
nhais_build_id = "develop-2-6659f4e"

# Settings for "OneOneOne" component
# Name changed to "OneOneOne" from "111" because of problems with some Terraform names starting with number
OneOneOne_service_minimal_count = 1
OneOneOne_service_desired_count = 2
OneOneOne_service_maximal_count = 4
OneOneOne_service_target_request_count = 1200
OneOneOne_service_container_port = 8080
OneOneOne_service_launch_type = "FARGATE"
OneOneOne_log_level = "DEBUG"
OneOneOne_build_id = "develop-2-6659f4e"
