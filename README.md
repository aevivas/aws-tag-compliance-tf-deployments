# Validating Tag Compliance for Terraform Deployments in AWS

Script to check that AWS managed resources in the terraform state file or terraform plan file are using the required tags for the deployment.

## Why?

You want to be sure that the tag policy defined in your organization is being enforced. It is easy to tag devices hence this script can provide you some assistance on identifying those AWS resources missing any of the tags.

## What formats of the state file and plan file are supported?

Currently only format version **4** for the state file and version **1.1** for the plan file are supported.

## Defining tag policy

You can define the *default_tags* tags to apply to all resources to be created in your deployment or if they are already deployed. 

In addition for a particular resource, you can define *addtional_tags* tags to checks or define *ignored_tags* to ignore a particular tag.

You needed to create a file named `.default_tags.yml` with the following content:

```
default_tags:
  - Tag1 
  - Tag2
  - Tag3

# Additional tags may be required by a particular resource(s).
addtional_tags:
  aws_iam_role:
    - Tag4

# Mandatory tags that can be ignored by a particular resource(s).
ignored_tags:
  aws_iam_policy:
    - Tag3
```



# Invoking the script

## Checking the state file

```
python application.py --input_type state --input_file terraform.tfstate
```

## Checking the plan file

First you need to generate a json output of your terraform plan. You can use the following commands:

```
terraform plan -out terraform.plan
terraform show -json terraform.plan | jq > terraform.plan.formatted.json
```

and run 

```
python application.py --input_type plan --input_file terraform.plan.formatted.json
```

For more information about other arguments, invoke the script `python application.py`.

## Results


The example below shows findings from the script:

```
------------------------------
name          : example
arn           : arn:aws:iam::111122223333:policy/example_policy
type          : aws_iam_policy
current tags  : Tag1, Tag2, Tag5
required tags : Tag1, Tag2
missing tags  : -
tag compliance: Passed
------------------------------
name          : example
arn           : arn:aws:iam::111122223333:role/example_role
type          : aws_iam_role
current tags  : Tag1, Tag2
required tags : Tag1, Tag2, Tag3, Tag4
missing tags  : Tag3, Tag4
tag compliance: Failed
------------------------------
name          : example2
arn           : arn:aws:iam::111122223333:role/example2_role
type          : aws_iam_role
current tags  : Tag1, Tag2, Tag3, Tag4
required tags : Tag1, Tag2, Tag3, Tag4
missing tags  : -
tag compliance: Passed
---------------------------------------------------------------
Summary: 1 out of 3 managed resources is not in tag-compliance.
```
