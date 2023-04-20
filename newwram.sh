#!/bin/bash

# Check for root privileges
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root"
    exit 1
fi

# Update package repositories and install required packages
echo "Updating package repositories and installing required packages..."
opkg update
opkg install docker git e2fsprogs fdisk

# Find the USB drive
echo "Detecting USB drive..."
usb_drive=$(find /sys/block/*/ -name "*sd*" | grep -o -m 1 'sd[a-z]\+')
if [ -z "$usb_drive" ]; then
    echo "No USB drive found. Please plug in a USB drive and try again."
    exit 1
fi

usb_mount_point="/mnt/usb"

# Format the USB drive if needed
read -p "Format the USB drive (all data will be lost) (y/N)? " format_usb
if [[ "$format_usb" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Formatting the USB drive and creating swap partition..."
    umount /dev/"$usb_drive"1
    swap_end=$(( 8 * 1024 * 1024 * 1024 / 512 + 2048 ))
    echo -e "o\nn\np\n1\n2048\n${swap_end}\nt\n82\nn\np\n2\n$((swap_end + 1))\n\nw" | fdisk /dev/"$usb_drive"
    echo "y" | mkfs.ext4 /dev/"$usb_drive"2
fi

# Set up swap space
echo "Setting up swap space on the USB drive..."
mkswap /dev/"$usb_drive"1
swapon /dev/"$usb_drive"1
echo "/dev/${usb_drive}1 none swap sw 0 0" >> /etc/fstab

# Mount the USB drive
echo "Mounting the USB drive..."
mkdir -p "$usb_mount_point"
mount /dev/"$usb_drive"2 "$usb_mount_point"

# Configure Docker to use the USB drive
echo "Configuring Docker to use the USB drive..."
docker_storage_conf="/etc/docker/daemon.json"
mkdir -p "$(dirname "$docker_storage_conf")"
echo "{\"data-root\": \"$usb_mount_point/docker\"}" > "$docker_storage_conf"
/etc/init.d/docker restart

# Download the lightweight Kali Linux Docker image
echo "Downloading lightweight Kali Linux Docker image..."
docker pull kalilinux/kali-rolling

# Prompt for VNC password
read -s -p "Enter your VNC password: " vnc_password
echo

# Create a Docker container and set up a VNC server
echo "Creating Docker container and setting up a VNC server..."
docker run -it -d --name kali-container -p 5900:5900 -v "$usb_mount_point/kali-home:/root" kalilinux/kali-rolling

# Update Kali and install necessary packages for VNC
echo "Updating Kali and installing necessary packages for VNC..."
docker exec -it kali-container bash -c "apt-get update && apt-get install -y kali-linux-core tightvncserver"

# Configure the VNC server
echo "Configuring the VNC server..."
docker exec -it kali-container bash -c "mkdir /root/.vnc && echo '$vnc_password' | vncpasswd -f > /root/.vnc/passwd && chmod 600 /root/.vnc/passwd"

#Start the VNC server

echo "Starting the VNC server..."
docker exec -it kali-container bash -c "vncserver :0 -geometry 1280x800 -depth 24"

echo "VNC server is running on port 5900. Connect using your VNC client with the specified password."
