#!/usr/bin/python

# Dependencies
import sys
import os
import time
import json
import tarfile
import shutil
import requests
import subprocess

# Help text
if len(sys.argv) < 2:
    print "Usage:"
    print " python restore.py (indexname)"
    print " python restore.py (indexname) (elasticsearch host)"
    print " python restore.py (indexname) (elasticsearch host) (elasticsearch port)"
    exit(0)

# Get the elasticsearch server
if len(sys.argv) > 2:
    host = sys.argv[2]
    if len(sys.argv) > 3:
        port = sys.argv[3]
    else:
        port = "9200"
else:
    host = "localhost"
    port = "9200"
url = "http://%s:%s" % (host, port)
print "Using ElasticSearch at %s" % url

try:
    r = requests.get(url)
    if r.status_code is not 200:
        print "Error hitting ElasticSearch on %s, response code was %i" % (url, r.status_code)
        exit(1)
    else:
        print "Verified ElasticSearch server"
except:
    print "Unable to hit ElasticSearch on %s" % url
    exit(1)

# Check with the user
index = sys.argv[1]
print "Restoring index '%s'" % index
print "Ctrl+C now to abort..."

time.sleep(3)

# Check the index doesnt already exist
r = requests.get("%s/%s/_mapping" % (url, index))
if r.status_code != 404:
    print "The index already exists. Please ensure it does not exist first."
    print "This command can be executed to do this:"
    print "curl -XDELETE %s/%s" % (url, index)
    exit(1)


# Unzip the backup file
filename = "%s.tar.gz" % index
tar = tarfile.open(filename)
tar.extractall()
tar.close()

# Read the settings
settings_file = open("%s/settings" % index, "r")
settings = json.loads(settings_file.read())
settings_file.close()
settings = settings[index]["settings"]

# Read the schema
schema_file = open("%s/schema" % index, "r")
schema = json.loads(schema_file.read())
schema_file.close()
schema = schema[index]["mappings"]

# Create the index on the server
data={}
data["mappings"] = schema
data["settings"] = settings
r = requests.put("%s/%s" % (url, index), data=json.dumps(data))
if r.status_code != 200:
    print "Unable to put the index to the server (%i), aborting" % r.status_code
    print r.content
    exit(1)

time.sleep(2)

# Elastcidump
ed_input = "--input=%s/data.json" % index
ed_output = "--output=http://localhost:9200/%s" % index
subprocess.call(["elasticdump", ed_input, ed_output])


# Clean up the directory
shutil.rmtree(index)

print "Finished"