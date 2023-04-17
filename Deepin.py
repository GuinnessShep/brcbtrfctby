import os
import requests
import json

def verbose_system(cmd, message):
    print(message)
    os.system(cmd)

def setup_ngrok():
    verbose_system("wget -q -c -nc https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip", "Downloading ngrok...")
    verbose_system("unzip -qq -n ngrok-stable-linux-amd64.zip", "Unzipping ngrok...")
    verbose_system("chmod +x ngrok", "Setting ngrok executable permission...")

    # Authenticate ngrok with your token
    os.system("./ngrok authtoken your_ngrok_auth_token_here")

    # Create a background process for the ngrok tunnel
    os.system("./ngrok tcp 5900 &")

def setup_deepin_docker():
    # Download Deepin ISO
    verbose_system("wget -q https://cdimage.deepin.com/releases/23-Alpha2/deepin-desktop-community-23-Alpha2-amd64.iso", "Downloading Deepin ISO...")
    
    # Mount the ISO and copy the contents to a temporary directory
    verbose_system("mkdir -p /mnt/deepin-iso", "Creating mount directory...")
    verbose_system("mount -o loop deepin-desktop-community-23-Alpha2-amd64.iso /mnt/deepin-iso", "Mounting Deepin ISO...")
    verbose_system("mkdir -p deepin-extracted", "Creating extraction directory...")
    verbose_system("cp -r /mnt/deepin-iso/* deepin-extracted/", "Extracting Deepin ISO contents...")
    verbose_system("umount /mnt/deepin-iso", "Unmounting Deepin ISO...")

    # Create Dockerfile
    dockerfile_content = '''
FROM debian:buster

COPY deepin-extracted /deepin

RUN echo "deb [trusted=yes] file:/deepin /" > /etc/apt/sources.list.d/deepin.list && \\
    apt-get update && \\
    apt-get install -y --no-install-recommends deepin-core tigervnc-standalone-server tigervnc-common && \\
    apt-get clean && \\
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir -p /root/.vnc && \\
    echo "your_vnc_password_here" | vncpasswd -f > /root/.vnc/passwd && \\
    chmod 600 /root/.vnc/passwd

EXPOSE 5900

COPY start_deepin_vnc.sh /start_deepin_vnc.sh
RUN chmod +x /start_deepin_vnc.sh

CMD ["/start_deepin_vnc.sh"]
'''
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content.replace("your_vnc_password_here", "your_desired_vnc_password"))

    # Create start_deepin_vnc.sh
    start_deepin_vnc_script = '''
#!/bin/sh

export USER=root
vncserver :0 -localhost no -geometry 1280x720 -depth 24
tail -f /root/.vnc/*.log
'''

    with open("start_deepin_vnc.sh", "w") as f:
        f.write(start_deepin_vnc_script)

setup_deepin_docker()

# Build the Docker image
verbose_system("docker build -t deepin-docker .", "Building Deepin Docker image...")

# Run the Deepin Docker container with VNC
verbose_system("docker run -d -p 5900:5900  --name deepin-docker deepin-docker", "Running Deepin Docker container with VNC...")

#Set up ngrok

setup_ngrok()

#Get the ngrok tunnel URL
import requests
import json

print("Getting ngrok tunnel URL...")
response = requests.get("http://localhost:4040/api/tunnels")
tunnels = json.loads(response.text)["tunnels"]

for tunnel in tunnels:
    if tunnel["proto"] == "tcp":
        print("ngrok URL: {}".format(tunnel["public_url"]))
