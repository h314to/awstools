import string
import random
import unittest
from awstools import awsiot as iot


def random_string(lenght=8):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(lenght)])


class TestAwsIoT(unittest.TestCase):
    def test_create_and_delete_thing(self):
        """Test if Things can be accurately created and deleted"""

        # generate a random name for the Thing
        name = "Thing-" + random_string()

        # create the Thing
        thing = iot.create_thing(name)

        # check if it was created correctly
        thing_props = iot.describe_thing(thing)
        self.assertEqual(name, thing_props['thingName'])

        # check if the Thing can be deleted
        iot.delete_thing(thing)
        try:
            iot.describe_thing(thing)
        except Exception as e:
            self.assertTrue("%s not found" % name in e.message)

    def test_create_and_delete_certificates(self):
        """Test if Certificates can be accurately created and deleted"""

        # create certificate and check that the description is correct, and that it is active
        cert = iot.create_keys_and_certificate()
        cert_desc = iot.describe_certificate(cert)
        self.assertEqual(cert['certificateArn'], cert_desc['certificateArn'])

        self.assertEqual(cert_desc['status'], "ACTIVE")

        # delete a certificate and check
        iot.delete_certificate(cert)
        try:
            iot.describe_certificate(cert)
        except Exception as e:
            self.assertTrue("%s does not exist" % cert['certificateId'] in e.message)

    def test_create_and_delete_policies(self):
        """Test if policies can be created and removed"""

        name = "Policy-" + random_string()

        # create policy and check that the correct properties can be retrieved from AWS
        pol = iot.create_policy(name, "Allow", "iot:Publish", "test")
        pol_desc = iot.get_policy(pol)

        self.assertEqual(pol["policyArn"], pol_desc["policyArn"])

        # delete polilcy and check it is gone
        iot.delete_policy(pol)
        try:
            iot.get_policy(pol)
        except Exception as e:
            self.assertTrue("ResourceNotFoundException" in e.message)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAwsIoT)
    unittest.TextTestRunner(verbosity=2).run(suite)
