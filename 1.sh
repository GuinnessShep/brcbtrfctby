#!/bin/bash
set -e

# Setup environment
echo "Setting up environment..."
apt-get update
apt-get install -y --no-install-recommends git curl wget

# Install Miniconda
echo "Installing Miniconda..."
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o Miniconda3.sh
bash Miniconda3.sh -bfp /usr/local

# Update PATH for conda
export PATH="/usr/local/bin:$PATH"

# Create a new conda environment
conda create -y -n textgen_env python=3.10.9
source activate textgen_env

# Install necessary packages
echo "Installing necessary packages..."
conda install -y accelerate sentencepiece
pip install torch torchvision torchaudio gradio

# Clone the text-generation-webui repository
echo "Cloning text-generation-webui repository..."
cd "$(dirname "$0")"
git clone https://github.com/oobabooga/text-generation-webui
cd text-generation-webui

# Install the requirements and deepspeed
echo "Installing requirements and deepspeed..."
pip install -r requirements.txt
pip install deepspeed

# Clone GPTQ-for-LLaMa repository and install
echo "Cloning GPTQ-for-LLaMa repository and installing..."
cd "$(pwd)/repositories"
rm -rf GPTQ-for-LLaMa
pip uninstall -y quant-cuda
git clone https://github.com/oobabooga/GPTQ-for-LLaMa -b cuda
cd GPTQ-for-LLaMa
python setup_cuda.py install

# Download and set up tunnelto
echo "Downloading and setting up tunnelto..."
cd "$(dirname "$0")/text-generation-webui"
wget -nc https://github.com/agrinman/tunnelto/releases/download/0.1.18/tunnelto-linux.tar.gz
tar -xvf tunnelto-linux.tar.gz
chmod +x tunnelto

# Create start_servers.sh script
echo "Creating start_servers.sh script..."
cat > start_servers.sh << 'EOL'
#!/bin/bash
python server.py --auto-devices --chat --gpu-memory 17 10 --cpu-memory 80 --xformers --share &
sleep 5
./tunnelto set-auth --key CeLFVxWt115kuo54j6HMkb &
sleep 5
./tunnelto --host 127.0.0.1 --port 7860 --subdomain ieatdoggyshit &
while true; do sleep 1; done
EOL

chmod +x start_servers.sh

# Run start_servers.sh
echo "Running start_servers.sh..."
./start_servers.sh

# Note: The script execution will continue running until you manually stop it.
