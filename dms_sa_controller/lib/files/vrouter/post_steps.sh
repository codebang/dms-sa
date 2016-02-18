#!/bin/bash
echo "post actions"
sudo journalctl -f | log-courier -config /etc/log-courier/log-courier.conf -stdin &

