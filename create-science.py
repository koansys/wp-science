#!/usr/bin/env python
# We expect to have set in our environment:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY

# TODO:
# - specify AZ
# - specify Instance size: t1.micro, m1.small (4x), m1.medium (2x)

import boto.ec2
import logging
import os
import time

IMAGE_ID = 'ami-3fec7956'       # Ubuntu 12.04 LTS
KEY_NAME = 'wp-science_key_3'
REGION = 'us-east-1'
INSTANCE_600MB = 't1.micro'
INSTANCE_2GB   = 'm1.small'
INSTANCE_4GB   = 'm1.medium'
INSTANCE_8GB   = 'm1.large'
AZ_LEFT  = 'us-east-1a'
AZ_RIGHT = 'us-east-1b'         # or -1c
SECURITY_GROUPS = ['WP-SCIENCE-EAST']
TAG_APP_KEY = 'APP'
TAG_APP_VAL = 'science.nasa.gov'   # add value to node's role (app, adm, db)
TAG_NAME_KEY = 'Name'              # lowercase seems what the Edit field wants
TAG_ROLE_KEY = 'ROLE'

INSTANCES = {                   # key on Name that we set as tag and present in Console
    'science-left-app'  : {'az': AZ_LEFT,  'type': INSTANCE_4GB, 'role': 'app'},
    'science-left-adm'  : {'az': AZ_LEFT,  'type': INSTANCE_4GB, 'role': 'adm'},
    'science-left-db'  :  {'az': AZ_LEFT,  'type': INSTANCE_8GB, 'role': 'db' },
    'science-right-app' : {'az': AZ_RIGHT, 'type': INSTANCE_4GB, 'role': 'app'},
    'science-right-adm' : {'az': AZ_RIGHT, 'type': INSTANCE_4GB, 'role': 'adm'},
    'science-right-db ' : {'az': AZ_RIGHT, 'type': INSTANCE_8GB, 'role': 'db' },
    }

logging.basicConfig(level=logging.INFO)

ec2 = boto.ec2.connect_to_region(REGION)

zones = ec2.get_all_zones()
logging.info('Zones: %s' % zones)

# should look for a science pair and if none, create and save it.
# boto.ec2.securitygroup...
key_pair = ec2.get_key_pair(KEY_NAME)
logging.info('Key pair: %s' % key_pair)

#key_pair = ec2.create_key_pair(KEY_NAME)
#key_pair.save(os.path.expanduser(os.path.join('~', '.ssh')))

for name, settings in INSTANCES.items():
    reservation = ec2.run_instances(instance_type=settings['type'],
                                    placement=settings['az'],
                                    user_data='NAME=%s' % name, # How best to use?
                                    image_id=IMAGE_ID,
                                    key_name=KEY_NAME,
                                    security_groups=SECURITY_GROUPS,
                                    )

    instance = reservation.instances[0] # We MUST only create one instance at a time, above
    logging.info('Name=%s %s %s' % (name, reservation, instance))

    # Can we request all reservations then check each one for its 'ready' instances matches us?
    logging.info('get_all_instances reservatons: %s' % ec2.get_all_instances()) # useless?

    # Wait for it to boot
    # Even after waiting, we sometimes see it not find the instance:
    #   boto.exception.EC2ResponseError: EC2ResponseError: 400 Bad Request
    #   InvalidInstanceID.NotFound</Code><Message>The instance ID 'i-c6d5d6a8' does not exist

    while True:
        # Loop FOREVER :-( on trying to get the instance info, it may not *really* be ready
        try:
            status = instance.update()
        except boto.exception.EC2ResponseError, e:
            logging.warning('While looking for instance.update(), try again: %s' % e)
            time.sleep(1)
        break

    while status == 'pending':
        logging.info('Sleeping on status=%s' % status)
        time.sleep(5)
        status = instance.update()
    if status != 'running':
        raise RuntimeError, 'Instance status != pending|running: %s' % status
    logging.info('Public DNS: %s' % instance.public_dns_name) 

    # Tag with application name (all instances belonging to one app), role, name for Console
    instance.add_tag(TAG_APP_KEY, TAG_APP_VAL)
    instance.add_tag(TAG_NAME_KEY, name)
    instance.add_tag(TAG_ROLE_KEY, settings['role'])
    # conn.create_tags([instance_ids], tag_dict)


#rets = ec2.terminate_instances(instance_ids=None)
