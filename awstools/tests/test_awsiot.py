import sh
import json
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
        pol_desc = iot.describe_policy(pol)

        self.assertEqual(pol["policyArn"], pol_desc["policyArn"])

        # delete polilcy and check it is gone
        iot.delete_policy(pol)
        try:
            iot.describe_policy(pol)
        except Exception as e:
            self.assertTrue("ResourceNotFoundException" in e.message)

    def test_attach_and_delete(self):
        """Test if:
          * policies can be attached to certificates
          * certificates can be attached to things
          * we can detach and delete certificates
          """
        thing_name = "Thing-" + random_string()
        policy_name = "Policy-" + random_string()

        thing = iot.create_thing(thing_name)
        certs = iot.create_keys_and_certificate()
        policy = iot.create_policy(policy_name, "Allow", "iot:Publish", "topic-" + random_string())
        arn = certs["certificateArn"]

        # attach policy and test if it is there
        iot.attach_policy(certs, policy)
        policies_data = json.loads(str(sh.aws("iot", "list-principal-policies", "--principal", arn)))
        attached_policy_name = policies_data["policies"][0]["policyName"]
        self.assertEqual(policy_name, attached_policy_name)

        # attach thing and test if it is there
        iot.attach_to_thing(thing, certs)
        things_data = json.loads(str(sh.aws("iot", "list-principal-things", "--principal", arn)))
        attached_thing_name = things_data["things"][0]
        self.assertEqual(thing_name, attached_thing_name)

        # delete certificate and make sure it is gone
        iot.delete_certificate(certs)
        try:
            iot.describe_certificate(certs)
        except Exception as e:
            self.assertTrue("%s does not exist" % certs['certificateId'] in e.message)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAwsIoT)
    unittest.TextTestRunner(verbosity=2).run(suite)
