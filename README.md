# Validating Tag Compliance for Terraform Deployments in AWS

Script to check that AWS managed resources in the terraform state file or terraform plan file are using the required tags for the deployment.

## Why?

You want to be sure that the tag policy defined in your organization is being enforced. It is easy to tag devices hence this script can provide you some assistance on identifying those AWS resources missing any of the tags.

## What formats of the state file and plan file are supported?

Currently, format version **4** for the state file, and version **1.1** for the plan file are supported.

## Defining tag policy

You can define the *default_tags* tags to apply to all resources to be created in your deployment or if they are already deployed. 

In addition for a particular resource, you can define *addtional_tags* tags to checks or define *ignored_tags* to ignore a particular tag.

You needed to create the file `.default_tags.yml` with similar content as shown below:

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

Check for *examples* folder for more details.


# Invoking the script

## Checking the state file

```
python application.py -v --input_type state --input_file terraform.tfstate 
```

## Checking the plan file

First you need to generate a json output of your terraform plan. You can use the following commands:

```
terraform plan -out terraform.plan
terraform show -json terraform.plan | jq > terraform.plan.json
```

and then run 

```
python application.py -v --input_type state --input_file terraform.plan.json 
```

For more information about other arguments, invoke the script `python application.py --help`.

## Checking tag compliance in the plan file

You can try the script with content of the examples folder. 

By running  

```
python application.py -v \
    --input_type plan \
    --input_file ./examples/terraform.plan.json \
    --tag_file ./examples/default_tags.yml
```

you will get the following output:

```
Fetching managed AWS resources from Plan file.
----------------------------------------------------------------------
address       : aws_iam_policy.policy_1
name          : policy_1
type          : aws_iam_policy
current tags  : Compliance, Department, Description, Environment, Owner, Version
required tags : Owner, Environment, Department, Compliance, Version, Description
missing tags  : -
tag compliance: Passed
----------------------------------------------------------------------
address       : aws_iam_policy.policy_1_1
name          : policy_1_1
type          : aws_iam_policy
current tags  : Compliance, Department, Environment, Owner, Version
required tags : Owner, Environment, Department, Compliance, Version, Description
missing tags  : Description
tag compliance: Failed
----------------------------------------------------------------------
address       : aws_iam_role.role_1
name          : role_1
type          : aws_iam_role
current tags  : Compliance, Department, Environment, Owner
required tags : Owner, Environment, Department, Compliance
missing tags  : -
tag compliance: Passed
----------------------------------------------------------------------
address       : aws_iam_role.role_2
name          : role_2
type          : aws_iam_role
current tags  : Department, Environment, Owner
required tags : Owner, Environment, Department, Compliance
missing tags  : Compliance
tag compliance: Failed
----------------------------------------------------------------------
Summary: 2 out of 4 managed resources are not in tag-compliance.
```

## Checking tag compliance in the state file

Likewise, by running:

```
python application.py -v \
    --input_type state \
    --input_file ./examples/terraform.tfstate  \
    --tag_file ./examples/default_tags.yml
```

you should get the following output:

```
etching managed AWS resources from State file.
----------------------------------------------------------------------
name          : policy_1
arn           : arn:aws:iam::4468********:policy/example_policy_1
type          : aws_iam_policy
current tags  : Compliance, Department, Description, Environment, Owner, Version
required tags : Owner, Environment, Department, Compliance, Version, Description
missing tags  : -
tag compliance: Passed
----------------------------------------------------------------------
name          : policy_1_1
arn           : arn:aws:iam::4468********:policy/example_policy_1_1
type          : aws_iam_policy
current tags  : Compliance, Department, Environment, Owner, Version
required tags : Owner, Environment, Department, Compliance, Version, Description
missing tags  : Description
tag compliance: Failed
----------------------------------------------------------------------
name          : role_1
arn           : arn:aws:iam::4468********:role/example_role1
type          : aws_iam_role
current tags  : Compliance, Department, Environment, Owner
required tags : Owner, Environment, Department, Compliance
missing tags  : -
tag compliance: Passed
----------------------------------------------------------------------
name          : role_2
arn           : arn:aws:iam::4468********:role/example_role2
type          : aws_iam_role
current tags  : Department, Environment, Owner
required tags : Owner, Environment, Department, Compliance
missing tags  : Compliance
tag compliance: Failed
----------------------------------------------------------------------
Summary: 2 out of 4 managed resources are not in tag-compliance.
```

## Loggging

After either run, the script will create the log file *application.plan.log* if you were checking tag compliance on the plan file; likewise, it will will create the log file *application.state.log* if you were checking tag compliance in the state file.