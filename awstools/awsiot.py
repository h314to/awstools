import os
import sh
import json
import configparser


def read_config(profile="default"):
    """
    Read the region and keys from the user's configuration files

    :param profile: the profile from which to read data
    :return: tuple with the id, region, key, and secret
    """
    awsid = sh.aws("sts", "get-caller-identity", "--output", "text", "--query", "Account").strip()

    config = configparser.RawConfigParser()

    try:
        config.read('%s/.aws/config' % os.environ['HOME'])
        region = config.get(profile, 'region')
    except:
        print("Error reading the '~/.aws/config' file.")
        raise

        # check if the user has defined his credentials
    try:
        config.read('%s/.aws/credentials' % os.environ['HOME'])
        key = config.get(profile, 'aws_access_key_id')
        secret = config.get(profile, 'aws_secret_access_key')
    except:
        print("Error reading the '~/.aws/credentials' file.")
        raise
    return awsid, region, key, secret


def arn_base():
    """
    Get the Amazon Resource Name (ARN) prefix for IoT

    :return: the ARN prefix
    """
    awsid, region, key, secret = read_config()
    return "arn:aws:iot:%s:%s:" % (region, awsid)


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
    # inactivate certificate
    sh.aws("iot", "update-certificate", "--certificate-id", id, "--new-status", "INACTIVE")

    arn = describe_certificate_by_id(id)["certificateArn"]

    # detach all policies
    policies_data = json.loads(str(sh.aws("iot", "list-principal-policies", "--principal", arn)))
    for policy in policies_data["policies"]:
        sh.aws("iot", "detach-principal-policy", "--policy-name", policy["policyName"], "--principal", arn)

    # detach all things
    things_data = json.loads(str(sh.aws("iot", "list-principal-things", "--principal", arn)))
    for thing in things_data["things"]:
        sh.aws("iot", "detach-thing-principal", "--thing-name", thing, "--principal", arn)

    # we safely delete certificate now
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


def create_policy(name, effect, action, topic):
    """

    :param name: policy name
    :param effect: policy effect ("Allow" or "Deny")
    :param action: action allowed or denied by policy (e.g. "iot:Publish", "iot:Connect", "iot:Subscribe")
    :param topic: topic on which the policy takes effect
    :return: dictionary with the policy properties
    """
    policy = dict(Version="2012-10-17")
    policy["Statement"] = [dict(Effect=effect, Action=[action], Resource=[arn_base() + "topic/" + topic])]
    return create_policy_from_string(name, str(json.dumps(policy)))


def create_policy_from_string(name, doc):
    """
    Create a policy

    :param name: policy name
    :param doc: json document string describing the policy
    :return: dictionary with the policy properties
    """
    response = sh.aws("iot", "create-policy", "--policy-name", name, "--policy-document", doc)
    return json.loads(str(response))


def describe_policy(policy):
    """
    Get policy document (json)

    :param name: policy name
    :return: dictionary with the policy properties
    """
    return describe_policy_by_name(policy['policyName'])


def describe_policy_by_name(name):
    """
    Get policy document (json) by specifying its name

    :param name: policy name
    :return: dictionary with the policy properties
    """
    response = sh.aws("iot", "get-policy", "--policy-name", name)
    return json.loads(str(response))


def delete_policy(policy):
    """
    Delete a policy

    :param policy: policy properties dictionary
    :return: None
    """
    delete_policy_by_name(policy['policyName'])


def delete_policy_by_name(name):
    """
    Delete a policy by specifying its name

    :param name: policy name
    :return: None
    """
    sh.aws("iot", "delete-policy", "--policy-name", name)


def attach_policy(certificate, policy):
    """
    Attach a policy to a certificate

    :param certificate: certificate json data
    :param policy: policy json data
    :return: None
    """
    attach_policy_by_arn_and_name(certificate["certificateArn"], policy["policyName"])


def attach_policy_by_arn_and_name(certificate_arn, policy_name):
    """
    Attach a policy to a certificate (using arn and name)

    :param certificate_arn: arn of the certificate
    :param policy_name: the policy hame
    :return:
    """
    sh.aws("iot", "attach-principal-policy", "--principal", certificate_arn, "--policy-name", policy_name)


def attach_to_thing(thing, certificate):
    """
    Attach certificate to a thing

    :param thing: thing json data
    :param certificate: certificate json data
    :return: None
    """
    attach_to_thing_by_arn_and_name(thing["thingName"], certificate["certificateArn"])


def attach_to_thing_by_arn_and_name(thing_name, certificate_arn):
    """
    Attach certificate to a thing (using arn and name)

    :param certificate_arn: arn of the certificate
    :param thing_name: the thing hame
    :return:
    """
    sh.aws("iot", "attach-thing-principal", "--principal", certificate_arn, "--thing-name", thing_name)
