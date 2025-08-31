git pull
systemctl daemon-reload
systemctl restart mb_vol_select_bot
journalctl -u mb_vol_select_bot -f