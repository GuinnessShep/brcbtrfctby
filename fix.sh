#!/bin/bash

# Function to check for and move any packages with unmet dependencies
function check_dependencies {
    echo "Checking for unmet dependencies..."
    pkgs=$(dpkg -l | grep ^i | awk '{print $2}')
    for pkg in $pkgs; do
        if ! apt-cache show $pkg &> /dev/null; then
            echo "$pkg has unmet dependencies, moving to /var/tmp..."
            mv /var/cache/apt/archives/$pkg*.deb /var/tmp/
        fi
    done
    echo "Done checking for unmet dependencies."
}

# Check for and move any packages with unmet dependencies
check_dependencies

# Remove any problematic packages
echo "Removing problematic packages..."
apt-get remove --purge -y libnvidia-compute-530 libnvidia-gl-530 nvidia-compute-utils-530 nvidia-utils-530

# Clean up any remaining packages and dependencies
echo "Cleaning up remaining packages and dependencies..."
apt-get -y autoremove
apt-get -y autoclean

# Install missing dependencies
echo "Installing missing dependencies..."
apt-get install -y libnvidia-compute-530 libnvidia-gl-530 nvidia-compute-utils-530 nvidia-utils-530 --fix-broken --force-yes

# Update the system
echo "Updating the system..."
apt-get -y update && apt-get -y upgrade

echo "Done!"
