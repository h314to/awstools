import os
import sh
import json
import ConfigParser


class AwsIoT:
    """AWS IoT connection """

    def read_config(self, profile="default"):
        # read the region from the user's configuration file, which should exist
        config = ConfigParser.RawConfigParser()
        try:
            config.read('%s/.aws/config' % os.environ['HOME'])
            region = config.get(profile, 'region')
        except:
            print "Error reading the '~/.aws/config' file."
            raise

            # check if the user has defined his credentials
        try:
            config.read('%s/.aws/credentials' % os.environ['HOME'])
            key = config.get(profile, 'aws_access_key_id')
            secret = config.get(profile, 'aws_secret_access_key')
        except:
            print "Error reading the '~/.aws/credentials' file."
            raise
        return region, key, secret

    def create_thing(self, name):
        """
        Create a Thing in the configured region
        :param name: name of the Thing
        :return: the properties of this thing
        """
        response = sh.aws("iot", "create-thing", "--thing-name", name)
        return json.loads(str(response))

    def delete_thing(self, thing):
        """
        Delete a Thing in the configured region
        :param thing: name of the Thing
        :return: None
        """
        self.delete_thing_by_name(thing['thingName'])

    def delete_thing_by_name(self, name):
        """
        Delete a Thing in the configured region by specifying its name
        :param name: name of the Thing
        :return: None
        """
        sh.aws("iot", "delete-thing", "--thing-name", name)

    def describe_thing(self, thing):
        """
        Get Thing properties
        :param thing:  json properties of the Thing
        :return: dictionary with the Thing's description
        """
        return self.describe_thing_by_name(thing['thingName'])

    def describe_thing_by_name(self, name):
        """
        Get Thing properties by specifying its name
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

    def delete_certificate(self, cert):
        """
        Inactivate and delete a certificate
        :param cert: the certificate json data
        :return: None
        """
        self.delete_certificate_by_id(cert['certificateId'])

    def delete_certificate_by_id(self, id):
        """
        Inactivate and delete a certificate with the given id
        :param id: the certificateID
        :return: None
        """
        sh.aws("iot", "update-certificate", "--certificate-id", id, "--new-status", "INACTIVE")
        sh.aws("iot", "delete-certificate", "--certificate-id", id)

    def describe_certificate(self, cert):
        """
        Get certificate info for the given id
        :param cert: the certificateId
        :return: dictionary with certificate properties
        """
        return self.describe_certificate_by_id(cert['certificateId'])

    def describe_certificate_by_id(self, id):
        """
        Get certificate info for the given id
        :param id: the certificateId
        :return: dictionary with certificate properties
        """
        response = sh.aws("iot", "describe-certificate", "--certificate-id", id)
        return json.loads(str(response))['certificateDescription']

    def write_keys_and_certificates(self, cert, path=os.environ['PWD']):
        """
        Write the certificate and keys to files
        :param cert: json with the certificate and keys
        :param path: output path (default: $PWD)
        :return: None
        """

        base_filename = path + "/" + cert['certificateId'][:10]

        certpem_file = open("%s-certificate.pem.crt" % base_filename, 'w')
        certpem_file.write(cert['certificatePem'])
        certpem_file.close()

        pubkey_file = open("%s-public.pem.key" % base_filename, 'w')
        pubkey_file.write(cert['keyPair']['PublicKey'])
        pubkey_file.close()

        privatekey_file = open("%s-private.pem.key" % base_filename, 'w')
        privatekey_file.write(cert['keyPair']['PrivateKey'])
        privatekey_file.close()
