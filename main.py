#!/usr/bin/env python

from AwsIoT import AwsIoT

iot = AwsIoT()


cert = iot.create_keys_and_certificate()
print cert
print cert['certificateId']
desc = iot.describe_certificate(cert)
print desc
iot.delete_certificate(cert)
