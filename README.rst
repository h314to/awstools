.. image:: https://readthedocs.org/projects/awstools/badge/?version=latest
  :target: http://awstools.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

awstools
========

This is a quick and simple API for AWS IoT based on the excellent awscli_ and sh_ packages.

.. _awscli: https://github.com/aws/aws-cli
.. _sh: https://github.com/amoffat/sh

Usage
-----

.. code:: python

    from awstools import awsiot as iot

    # Create things, certificate, keys, and policy
    thing = iot.create_thing("DummyThing")
    certs = iot.create_keys_and_certificate()
    policy = iot.create_policy("PubToDummy", "Allow", "iot:Publish", "dummy")

    # Save certificates and keys
    iot.write_keys_and_certificates(certs)

    # Attach policy to certs
    iot.attach_policy(certs, policy)

    # Attach certs to thing
    iot.attach_to_thing(thing, certs)

For more information please see the documentation_.

.. _documentation: http://awstools.readthedocs.io/
