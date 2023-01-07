import json
import yaml
import argparse
from termcolor import colored
import logging


class AwsResource(object):

    def __init__(self, tag_policy: dict):
        self.tag_policy = tag_policy

    def __call__(
            self,
            resource):

        self.rtype = resource['rtype']
        self.name = resource['name']
        self.module = resource.get('module', None)
        self.address = resource.get('address', None)
        self.arn = resource.get('arn', None)
        self.tags = self.list_tag_name_from_tags(resource['tags'])
        self.tags_all = self.list_tag_name_from_tags(resource['tags_all'])

    def get_all_tags(self) -> list:
        """Getting all the tags associated to a resources by
        combining the resources tags and the provider tags in
        on list.

        Returns:
            list: List of tags applied to a resource.
        """

        tags_list = self.tags
        [tags_list.append(t) for t in self.tags_all if t not in tags_list]
        tags_list.sort()

        return tags_list

    def get_formatted_address(self) -> str:

        if self.address:
            return self.address

        address = f"{self.rtype}.{self.name}"

        if self.module:
            address = f"{self.module}.{address}"

        return address

    def list_missing_tags(self) -> list:
        required_tags = self.get_required_tags()
        all_tags_resources = self.get_all_tags()

        missing_tag_list = []

        for required_tag in required_tags:
            if required_tag not in all_tags_resources:
                missing_tag_list.append(required_tag)

        return missing_tag_list

    def list_tag_name_from_tags(self, tags) -> list:
        """Returns a list of the tag keys. Empty list if
        there are no tags.

        Args:
            tags (dict): dictionary with the tags.

        Returns:
            list: list of tag keys
        """

        # The tag key can exists in the datafile with null value
        if type(tags) is not dict:
            return []

        return list(tags.keys())

    def tag_compliance_valid_status(self) -> bool:
        """Validating the tag compliance for the resource by checking
        if there is a tags missing.

        Returns:
            bool: True if in complaince, otherwise False
        """
        if self.list_missing_tags():
            return False
        else:
            return True

    def show_info(self, verbosity):

        if verbosity >= 1:
            print("-" * 70)

            if self.module:
                print(f"module        : {self.module}")
            if self.address:
                print(f"address       : {self.address}")
            print(f"name          : {self.name}")
            if self.arn:
                print(f"arn           : {self.arn}")
            print(f"type          : {self.rtype}")
            print(f"current tags  : {', '.join(self.get_all_tags())}")
            print(f"required tags : {', '.join(self.get_required_tags())}")

            list_missing_tags = ', '.join(
                self.list_missing_tags()) if self.list_missing_tags() else '-'
            print(f"missing tags  : {list_missing_tags}")

            if self.tag_compliance_valid_status():
                valid_status = colored('Passed', 'green')
            else:
                valid_status = colored('Failed', 'red')
            print(f"tag compliance: {valid_status}")

        else:
            if self.tag_compliance_valid_status():
                valid_status = colored('Passed', 'green')
            else:
                list_missing_tags = ', '.join(self.list_missing_tags())
                valid_status = f"{colored('Failed', 'red')} (tags missing: {list_missing_tags})"

            print(f"{self.  get_formatted_address()}: {valid_status}")

    def get_required_tags(self) -> list:
        """Getting the required tags for this type of resource

        Returns:
            list: Required tags
        """
        required_tags = self.tag_policy['default_tags'].copy()

        # # Including tags for this resource type.
        inclusion_tags = self.tag_policy.get('addtional_tags', None)
        if inclusion_tags:
            tags = inclusion_tags.get(self.rtype, [])
            if tags:
                for tag in tags:
                    if tag not in required_tags:
                        required_tags.append(tag)

        # Excluding tags for the resource type.
        exclusion_tags = self.tag_policy.get('ignored_tags', None)

        if exclusion_tags:
            if self.rtype in exclusion_tags.keys():
                tags = exclusion_tags.get(self.rtype, [])
                if tags:
                    for tag in tags:
                        if tag in required_tags:
                            required_tags.remove(tag)
        return required_tags


def get_managed_resources_from_statefile(data) -> list:
    """Getting all AWS managed resources from the state file

    Args:
        data (dict): content of the state file in json

    Raises:
        Exception: only format version #4 is supported

    Returns:
        list: List of managed AWS resources that can accept tags
    """

    statefile_format_version = data['version']

    if statefile_format_version != 4:
        msg = f"The state file format \"{statefile_format_version}\" is not supported."
        raise Exception(msg)

    resources = []
    for resource in data['resources']:
        resource_name = resource['name']

        logging.info(f"Details for resource: {resource_name}: {resource}")

        if resource['mode'] != 'managed':
            logging.info(
                f"Skipping {resource_name} because is not a managed resource")
            continue

        if resource['provider'] != "provider[\"registry.terraform.io/hashicorp/aws\"]":
            logging.info(f"Skipping {resource_name} because is not in AWS")
            continue

        if 'arn' not in resource['instances'][0]['attributes'].keys():
            logging.info(
                f"Skipping {resource_name} because it does not have ARN")
            continue

        if 'tags' not in resource['instances'][0]['attributes'].keys():
            logging.info(
                f"Skipping {resource_name} because it does not support tags")
            continue

        temp_res = {}
        temp_res['rtype'] = resource['type']
        temp_res['mode'] = resource['mode']
        temp_res['name'] = resource['name']
        temp_res['module'] = resource.get('module', None)
        temp_res['arn'] = resource['instances'][0]['attributes']['arn']
        temp_res['tags'] = resource['instances'][0]['attributes']['tags']
        temp_res['tags_all'] = resource['instances'][0]['attributes']['tags_all']

        logging.info(
            f"Selecting resource {resource_name} with extracted values: {temp_res}")

        resources.append(temp_res)

    return resources


def get_managed_resources_from_planfile(data) -> list:
    """Getting all AWS managed resources from the plan file

    Args:
        data (dict): content of the plan file in json

    Raises:
        Exception: only format version #1.1 is supported

    Returns:
        list: List of managed AWS resources that can accept tags
    """

    planfile_format_version = data['format_version']

    if planfile_format_version != "1.1":
        msg = f"The plan file format \"{planfile_format_version}\" is not supported."
        raise Exception(msg)

    all_resources = []

    # Fetching all resources at the root_module level
    root_module_resources = data['planned_values']['root_module'].get(
        'resources', [])

    if root_module_resources:
        all_resources += root_module_resources

    # Fetching all resources at the child_modules level. This
    # requires to loop thru every child_module and fetch the
    # resources for each child_module.
    child_modules = data['planned_values']['root_module'].get(
        'child_modules', [])
    if child_modules:
        for child_module in child_modules:
            resources = child_module.get('resources', [])
            if resources:
                all_resources += child_module['resources']

    resources = []

    for resource in all_resources:

        resource_name = resource['name']
        logging.info(f"Details for resource: {resource_name}: {resource}")

        if resource['provider_name'] != "registry.terraform.io/hashicorp/aws":
            logging.info(f"Skipping {resource_name} because is not in AWS")
            continue

        if 'tags' not in resource['values']:
            logging.info(
                f"Skipping {resource_name} because it does not support tags")
            continue

        temp_res = {}
        temp_res['rtype'] = resource['type']
        temp_res['name'] = resource['name']
        temp_res['address'] = resource['address']
        temp_res['tags'] = resource['values']['tags']
        temp_res['tags_all'] = resource['values'].get('tags_all', None)

        logging.info(
            f"Selecting resource {resource_name} with extracted values: {temp_res}")

        resources.append(temp_res)

    return resources


def validate_resources_tag_compliance(
        resources,
        tag_policy,
        verbosity):

    aws_resource = AwsResource(tag_policy)

    managed_resources = 0
    non_compliance_resources = 0

    for resource in resources:
        managed_resources += 1
        aws_resource(resource=resource)
        aws_resource.show_info(verbosity=verbosity)
        if not aws_resource.tag_compliance_valid_status():
            non_compliance_resources += 1

    # Showing a summary after looping thru all resources in the datafile.
    noun_number = 'resource' if managed_resources == 1 else 'resources'
    verb_conjugation = 'is' if non_compliance_resources == 1 else 'are'

    if non_compliance_resources == 0:
        message = f"Summary: all the {managed_resources} managed {noun_number} {verb_conjugation} in tag-compliance."
    else:
        message = f"Summary: {non_compliance_resources} out of {managed_resources} managed {noun_number} {verb_conjugation} not in tag-compliance."
    print('-' * 70)
    print(message)

    results = {
        'results':
            {
                'managed_resources': managed_resources,
                'non_compliance_resources': non_compliance_resources
            }
    }

    logging.info(f"compliance report: {results}")
    return results


def main(
        data,
        tag_policy,
        input_file,
        input_type,
        verbosity=0):

    if input_type == 'state':
        print("Fetching managed AWS resources from State file.")
        resources = get_managed_resources_from_statefile(data)
    elif input_type == 'plan':
        print("Fetching managed AWS resources from Plan file.")
        resources = get_managed_resources_from_planfile(data)
    else:
        print("File type not valid")
        raise

    validate_resources_tag_compliance(
        resources=resources,
        tag_policy=tag_policy,
        verbosity=verbosity)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='application.py',
        description='Validate that mandatory tags for resources exist in the state or plan file.')

    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0)

    parser.add_argument(
        '--input_type',
        choices=["state", "plan"],
        help="Indicating whether a state file or terraform plan will be evaluated.",
        required=True)

    parser.add_argument(
        '--input_file',
        required=True,
        help="Path to the state file or terraform plan file to be evaluated.")

    parser.add_argument(
        '--tag_file',
        default="./default_tags.yml",
        help="(default: %(default)s)")

    args = parser.parse_args()

    logging.basicConfig(filename=f'application.{args.input_type}.log',
                        filemode='w',
                        format='%(asctime)s,%(msecs)d %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    with open(args.tag_file, 'r') as f_config:
        tag_policy = yaml.load(f_config, Loader=yaml.FullLoader)

    logging.info(f"tag_policy: {tag_policy}")

    with open(args.input_file, 'r') as f_data:
        data = json.load(f_data)

    verbosity = args.verbosity

    main(
        data=data,
        tag_policy=tag_policy,
        input_type=args.input_type,
        input_file=args.input_file,
        verbosity=verbosity)
