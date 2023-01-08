#!/bin/zsh

# Automating the generation of the terraform plan and state files by 
# running an auto apply, and similarly deleting any deployed resource
# in AWS by running an auto destroy.

export AWS_PROFILE=your-aws-profile

terraform fmt
terraform plan -out terraform.plan
terraform show -json terraform.plan | jq | sed -r 's/:([0-9]{4})[0-9]+:/:\1********:/g' > terraform.plan.json > ../examples/terraform.plan.json

# Doing the deployment magic.
terraform apply -auto-approve terraform.plan

# Making a sanitazed copy of the state file with the aws account obfuscated.
sed -r 's/:([0-9]{4})[0-9]+:/:\1********:/g' terraform.tfstate > ../examples/terraform.tfstate

# Cleaning up things in AWS
terraform destroy -auto-approve
