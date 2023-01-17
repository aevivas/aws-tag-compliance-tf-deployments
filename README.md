# Validating Tag Compliance for Terraform Deployments in AWS

Script to check that AWS managed resources in the terraform state file or terraform plan file are using the required tags for the deployment. The required tags are based on workplace, or project preferences.

## Motivation

You want to be sure that the tag policy defined in your organization is being enforced. It is easy miss a tag when writing your terraform code; hence this script can provide you some assistance on identifying those AWS resources missing any of the required tags.

## Supported format versions for state and plan files

Currently, version **4** for the state file, and version **1.1** for the plan file are supported.

## Defining tag policy

You can define your tag policy by creating a file with the following sections:

### Default tags (required)

List the default tags to apply to all resources:

```
default_tags:
  - Tag1 
  - Tag2
  - Tag3
```

### Additional tags (optional)

Addional tags to apply to particular resource types

```
addtional_tags:
  resource_type:
    - Tag4
  resource_type:
    - Tag6
```

### Ignored tags (optional)

Tags that can be ignored for particular resource types

```
ignored_tags:
  resource_type:
    - Tag7
  resource_type:
    - Tag8
```

You can check the template `.default_tags.yml` in this folder for more details or the file `examples/.default_tags.yml` for an working example.


# Invoking the script

## Inspecting terraform state file for tag compliance

You can check the tag compliance in the state file by invoking the script as follows:

```
python application.py -v --input_type state --input_file terraform.tfstate 
```

## Inspecting terraform plan file for tag compliance

Before you can inspect the plan file, you need to generate a json output of your terraform plan using the following commands:

```
terraform plan -out terraform.plan
terraform show -json terraform.plan | jq > terraform.plan.json
```

Then you can check the tag compliance in the plan file by invoking the script as follows:

```
python application.py -v --input_type state --input_file terraform.plan.json 
```

The script will output the resources along with their compliance status.

For more information about other arguments, invoke the script `python application.py --help`.


# Trying the script

The *terraform* folder contains the configuration files you can use to generate a plan and state file. Navigate to the folder and run the script *./terraform.sh* (you need an AWS account). This script will create a plan file,execute and apply, and then destroy the resources; additionally, it will copy the just-created plan and state files to the *examples* folder.


## Checking tag compliance in the plan file

Run the script as shown below to check tag compliance of the just-created plan file by terraform.

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

Likewise, you can check the tag compliance in the state file by running:

```
python application.py -v \
    --input_type state \
    --input_file ./examples/terraform.tfstate  \
    --tag_file ./examples/default_tags.yml
```

you should get the following output:

```
Fetching managed AWS resources from State file.
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

## Logging

After either run, the script will create the log file *application.plan.log* if you were checking tag compliance in the plan file; likewise, it will will create the log file *application.state.log* if you were checking tag compliance in the state file.
