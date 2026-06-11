# Server-Setup später

Empfohlen:
- Ubuntu 24.04 LTS
- 4-8 vCPU
- 8-16 GB RAM oder mehr
- Deutschland als Standort

## Grundinstallation

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git ufw
sudo ufw allow OpenSSH
sudo ufw allow 8501/tcp
sudo ufw enable
```

## Projekt installieren

```bash
cd /opt
sudo mkdir dr_money_bot
sudo chown $USER:$USER dr_money_bot
cd dr_money_bot
# Dateien hochladen oder git clone nutzen
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
```

## Start

```bash
python -m app.main_bot
streamlit run app/dashboard/streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```
