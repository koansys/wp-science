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
SECURITY_GROUPS = ['WP-SCIENCE-EAST']
TAGS_KEY = 'science.nasa.gov'   # add value to node's role (app, adm, db)

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
# NO run_instance...
# How to specify AZ?
reservation = ec2.run_instances(image_id=IMAGE_ID,
                                key_name=KEY_NAME,
                                instance_type=INSTANCE_4GB,
                                security_groups=SECURITY_GROUPS,
                                )

logging.info('Reservation: %s id=%s' % (reservation, reservation.id))
# reservation.id=r-90925aed
# reservattion.instances = [Instance:i-bd4ebcd2]

instance = reservation.instances[0] # Assumes we've only created one at a time
logging.info('Instance: %s' % instance)

# Wait for it to boot
status = instance.update()
while status == 'pending':
    logging.info('Sleeping on status=%s' % status)
    time.sleep(5)
    status = instance.update()
if status != 'running':
    raise RuntimeError, 'Instance status != pending|running: %s' % status
instance.add_tag(TAGS_KEY, 'Blinded!')




logging.info('Public DNS: %s' % instance.public_dns_name) 

#r.add_tag(TAG_KEY, 'app/adm/db')
#ec2.get_all_instances()[0].instances[0].add_tag('SCIENCE', 'BLINDED')
# conn.create_tags(instance.id, tag_dict)

# TODO: give it a name: science-{app,adm,db}-{left,right}  [set as a tag NAME?]

#rets = ec2.terminate_instances(instance_ids=None)
