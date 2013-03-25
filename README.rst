============
 WP Science
============

Create a 6-instance architecture like our current one so we can
migrate Science. Like::

  AMI OS: Ubuntu Server 12.04 LTS
  SSH KEY: wp-science-east.pem
  Security Group: WP-SCIENCE-EAST (allow ssh, http, https)

  AZ=US-EAST-1a      AZ=US-EAST-1b        Instance type

  science-app-left   science-app-right    m1.medium (4GB RAM)
  science-adm-left   science-adm-right    m1.medium (4GB RAM)
  science-db-left    science-db-right     m1.large  (8GB RAM)



Then front with Elastic Load Balancer.

Finally serve via CloudFront CDN targetting the United States.

