import os
import sh
import json
import ConfigParser


class AwsIoT:
    """AWS IoT connection """

    def __init__(self, profile="default"):
        # read the region from the user's configuration file, which should exist
        config = ConfigParser.RawConfigParser()
        try:
            config.read('%s/.aws/config' % os.environ['HOME'])
            self.region = config.get(profile, 'region')
        except:
            print "Error reading the '~/.aws/config' file."
            raise

            # check if the user has defined his credentials
        try:
            config.read('%s/.aws/credentials' % os.environ['HOME'])
            self.region = config.get(profile, 'aws_access_key_id')
            self.region = config.get(profile, 'aws_secret_access_key')
        except:
            print "Error reading the '~/.aws/credentials' file."
            raise

    def create_thing(self, name):
        """
        Create a Thing in the configured region
        :param name: name of the Thing
        :return: the properties of this thing
        """
        response = sh.aws("iot", "create-thing", "--thing-name", name)
        return json.loads(str(response))

    def delete_thing(self, name):
        """
        Delete a Thing in the configured region
        :param name: name of the Thing
        """
        sh.aws("iot", "delete-thing", "--thing-name", name)

    def describe_thing(self, name):
        """
        Get Thing properties
        :param name:  name of the Thing
        :return: dictionary with the Thing's description
        """
        response = sh.aws("iot", "describe-thing", "--thing-name", name)
        return json.loads(str(response))

    def create_keys_and_certificate(self):
        """
        Create and activate keys and certificate
        :return: dictionary with the certificateArn, certificatePem, PublicKey, PrivateKey, and certificateId
        """
        response = sh.aws("iot", "create-keys-and-certificate", "--set-as-active")
        return json.loads(str(response))

    def delete_certificate(self, id):
        """
        Inactivate and delete a certificate
        :param id: the certificateID
        """
        sh.aws("iot", "update-certificate", "--certificate-id", id, "--new-status", "INACTIVE")
        sh.aws("iot", "delete-certificate", "--certificate-id", id)

    def describe_certificate(self, id):
        """
        Get certificate info
        :param id: the certificateId
        :return: dictionary with certificate properties
        """
        response = sh.aws("iot", "describe-certificate", "--certificate-id", id)
        return json.loads(str(response))['certificateDescription']
