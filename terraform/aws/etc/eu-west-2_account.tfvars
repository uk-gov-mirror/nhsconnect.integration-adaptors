ecr_repositories = [
  {
    name = "111",
    scan = false,
    expire_PR_after = 14,
    prefix_to_keep  = "master",
    number_to_keep  = 10
  },
  # {
  #   name = "nhais",
  #   scan = false,
  #   expire_PR_after = 14,
  #   prefix_to_keep = "develop"
  #   number_to_keep = 10
  # },
]

account_cidr_block = "10.10.0.0/16"