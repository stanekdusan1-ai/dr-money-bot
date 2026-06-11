# Systemd Dienste später

## Bot Service

`/etc/systemd/system/dr-money-bot.service`

```ini
[Unit]
Description=DR Money Telegram Bot
After=network.target

[Service]
WorkingDirectory=/opt/dr_money_bot
ExecStart=/opt/dr_money_bot/.venv/bin/python -m app.main_bot
Restart=always
User=root
EnvironmentFile=/opt/dr_money_bot/.env

[Install]
WantedBy=multi-user.target
```

## Dashboard Service

`/etc/systemd/system/dr-money-dashboard.service`

```ini
[Unit]
Description=DR Money Dashboard
After=network.target

[Service]
WorkingDirectory=/opt/dr_money_bot
ExecStart=/opt/dr_money_bot/.venv/bin/streamlit run app/dashboard/streamlit_app.py --server.address 0.0.0.0 --server.port 8501
Restart=always
User=root
EnvironmentFile=/opt/dr_money_bot/.env

[Install]
WantedBy=multi-user.target
```
