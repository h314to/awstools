import os
import sh
import json
import ConfigParser


def read_config(profile="default"):
    """
    Read the region and keys from the user's configuration files
    :param profile: the profile from which to read data
    :return: tuple with the region, the key, and the secret
    """
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


def create_thing(name):
    """
    Create a Thing in the configured region
    :param name: name of the Thing
    :return: the properties of this thing
    """
    response = sh.aws("iot", "create-thing", "--thing-name", name)
    return json.loads(str(response))


def delete_thing(thing):
    """
    Delete a Thing in the configured region
    :param thing: name of the Thing
    :return: None
    """
    delete_thing_by_name(thing['thingName'])


def delete_thing_by_name(name):
    """
    Delete a Thing in the configured region by specifying its name
    :param name: name of the Thing
    :return: None
    """
    sh.aws("iot", "delete-thing", "--thing-name", name)


def describe_thing(thing):
    """
    Get Thing properties
    :param thing:  json properties of the Thing
    :return: dictionary with the Thing's description
    """
    return describe_thing_by_name(thing['thingName'])


def describe_thing_by_name(name):
    """
    Get Thing properties by specifying its name
    :param name:  name of the Thing
    :return: dictionary with the Thing's description
    """
    response = sh.aws("iot", "describe-thing", "--thing-name", name)
    return json.loads(str(response))


def create_keys_and_certificate():
    """
    Create and activate keys and certificate
    :return: dictionary with the certificateArn, certificatePem, PublicKey, PrivateKey, and certificateId
    """
    response = sh.aws("iot", "create-keys-and-certificate", "--set-as-active")
    return json.loads(str(response))


def delete_certificate(cert):
    """
    Inactivate and delete a certificate
    :param cert: the certificate json data
    :return: None
    """
    delete_certificate_by_id(cert['certificateId'])


def delete_certificate_by_id(id):
    """
    Inactivate and delete a certificate with the given id
    :param id: the certificateID
    :return: None
    """
    sh.aws("iot", "update-certificate", "--certificate-id", id, "--new-status", "INACTIVE")
    sh.aws("iot", "delete-certificate", "--certificate-id", id)


def describe_certificate(cert):
    """
    Get certificate info for the given id
    :param cert: the certificateId
    :return: dictionary with certificate properties
    """
    return describe_certificate_by_id(cert['certificateId'])


def describe_certificate_by_id(id):
    """
    Get certificate info for the given id
    :param id: the certificateId
    :return: dictionary with certificate properties
    """
    response = sh.aws("iot", "describe-certificate", "--certificate-id", id)
    return json.loads(str(response))['certificateDescription']


def write_keys_and_certificates(cert, path=os.environ['PWD']):
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
