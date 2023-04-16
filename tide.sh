#!/bin/bash

# Define the version of aptitude to be installed
APTITUDE_VERSION=0.8.10-6

# Define the download URL for the aptitude binary
APTITUDE_URL=http://ftp.us.debian.org/debian/pool/main/a/aptitude/aptitude_${APTITUDE_VERSION}_amd64.deb

# Define the path to the downloaded binary file
APTITUDE_BINARY=aptitude_${APTITUDE_VERSION}_amd64.bin

# Download the aptitude binary
wget $APTITUDE_URL -O $APTITUDE_BINARY

# Extract the aptitude binary from the deb package
ar x $APTITUDE_BINARY
tar -xf data.tar.*

# Make the aptitude binary executable
chmod +x usr/bin/aptitude

# Run the aptitude binary
./usr/bin/aptitude
