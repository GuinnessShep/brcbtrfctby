apt-get update
apt-get install -y --no-install-recommends git curl wget
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o Miniconda3.sh
bash Miniconda3.sh -bfp /usr/local
export PATH="/usr/local/bin:$PATH"
conda install -y python=3.10.9
conda install -y accelerate sentencepiece torch gradio torchvision torchaudio
cd "$(dirname "$0")"
git clone https://github.com/oobabooga/text-generation-webui
cd text-generation-webui
pip install -r requirements.txt
pip install deepspeed
python setup_cuda.py install
cd "$(dirname "$0")/text-generation-webui"
wget -nc https://github.com/agrinman/tunnelto/releases/download/0.1.18/tunnelto-linux.tar.gz
tar -xvf tunnelto-linux.tar.gz
chmod +x tunnelto
./tunnelto set-auth --key CeLFVxWt115kuo54j6HMkb &
./tunnelto --host 127.0.0.1 --port 7860 --subdomain ieatdoggyshit 
