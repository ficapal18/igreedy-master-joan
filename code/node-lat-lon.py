#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import xmlrpclib, pprint
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

API_URL    = "https://www.planet-lab.eu:443/PLCAPI/"
AUTH = {
    'AuthMethod': 'password',
    'Username'  : 'danilo.cicalese@telecom-paristech.fr',
    'AuthString': 'sdbD:1989',
}

srv = xmlrpclib.ServerProxy(API_URL, allow_none=True)

nodes = srv.GetNodes(AUTH, {}, ['hostname', 'site_id'])
sites = srv.GetSites(AUTH, {}, ['site_id', 'latitude', 'longitude','address_ids','node_ids','abbreviated_name'])
addresses=srv.GetAddresses(AUTH, {}, ['address_id','city','country','postalcode'])

map_sites  = dict()
map_address= dict()

for address in addresses:
    map_address[address['address_id']] =address

count=0
for site in sites:

    try:
    
       for x in site['address_ids']:
            addressSites=map_address[x]
       map_sites[site['site_id']] =[site,addressSites]
    except :
       pass
print "#hostname\tlatitude\tlongitude\tcity\tcountry"

for node in nodes:
    site = map_sites[node['site_id']] #error city and country

    try:
        city=site[1].get('city')
        country= site[1].get('country')
    except :
        city="N/A"
        country="N/A"
    latitude = site[0].get('latitude')
    longitude = site[0].get('longitude')
    if not latitude: latitude = 0
    if not longitude: longitude = 0
    
    print "%s\t%f\t%f\t%s\t%s" % (node['hostname'], latitude, longitude,city,country)
