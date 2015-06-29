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
	print "	python backup.py (indexname)"
	print "	python backup.py (indexname) (elasticsearch host)"
	print "	python backup.py (indexname) (elasticsearch host) (elasticsearch port)"
	exit(1)

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
	if r.status_code != 200:
		print "Error hitting ElasticSearch on %s, response code was %i" % (url, r.status_code)
		exit(1)
	else:
		print "Verified ElasticSearch server"
except:
	print "Unable to hit ElasticSearch on %s" % url
	exit(1)

# Check with the user
index = sys.argv[1]
print "Backing up index '%s'" % index
print "Ctrl+C now to abort..."

time.sleep(3)

# Make the directories we need
print "Checking write permission to current directory"
try:
	os.mkdir(index)
	# os.mkdir("%s/data" % index)
except:
	print "Unable to write to the current directory, please resolve this and try again"
	exit(1)

# Download and save the settings
print "Downloading '%s' settings" % index

r = requests.get("%s/%s/_settings" % (url, index))
if r.status_code != 200:
        print "Unable to get settings for index '%s', error code: %i" % (index, r.status_code)
        exit(1)

settings_file = open("%s/settings" % index, "w")
settings_file.write(r.content)
settings_file.close()

# Download and save the schema
print "Downloading '%s' schema" % index

r = requests.get("%s/%s/_mapping" % (url, index))
if r.status_code != 200:
	print "Unable to get schema for index '%s', error code: %i" % (index, r.status_code)
	exit(1)

schema_file = open("%s/schema" % index, "w")
schema_file.write(r.content)
schema_file.close()

# Elastcidump
ed_input = "--input=http://localhost:9200/%s" % index
ed_output = "--output=%s/data.json" % index
subprocess.call(["elasticdump", ed_input, ed_output, "--type=data"])


# Zip up the data
filename = "%s.tar.gz" % index
tar = tarfile.open(filename, "w:gz")
tar.add(index)
tar.close()

# Delete the directory
shutil.rmtree(index)

print "Complete. Your file is:"
print filename
exit(0)

