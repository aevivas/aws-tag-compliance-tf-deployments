import unittest
import application

class TestResource(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

      cls.false = False
      cls.null = None

      cls.resource = {
        'rtype': 'aws_iam_policy', 
        'mode': 'managed', 
        'name': 'example', 
        'module': None, 
        'arn': 'arn:aws:iam::111111111111:policy/example_policy', 
        'tags': {'Tag5': 'Tag5'}, 
        'tags_all': {'Tag1': 'Tag1', 'Tag2': 'Tag2', 'Tag5': 'Tag5'}
      }

      cls.invalid_resource = {
        'rtype': 'aws_iam_policy', 
        'mode': 'managed', 
        'name': 'example', 
        'module': None, 
        'arn': 'arn:aws:iam::111111111111:policy/example_policy', 
        'tags': {'Tag1': 'Tag1'}, 
        'tags_all': {'Tag1': 'Tag1', 'Tag5': 'Tag5'}
      }

      cls.tag_policy = {
        'default_tags': [
          'Tag1', 
          'Tag2', 
          'Tag3'
        ], 
        'addtional_tags': {
            'aws_iam_role': ['Tag4']
        }, 
        'ignored_tags': {
            'aws_iam_policy': ['Tag3']
        }
      }

      cls.aws_resource = application.AwsResource(cls.tag_policy)


    def test_passed_tag_compliance_valid_status(self):
      self.aws_resource(resource=self.resource)
      status = self.aws_resource.tag_compliance_valid_status()
      self.assertTrue(status)

    def test_failed_tag_compliance_valid_status(self):
      self.aws_resource(resource=self.invalid_resource)
      status = self.aws_resource.tag_compliance_valid_status()
      self.assertFalse(status)

if __name__ == '__main__':
    unittest.main()