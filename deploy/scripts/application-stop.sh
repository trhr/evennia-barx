#!/bin/bash
export LOGFILE=/home/ec2-user/barx/deploylog
touch "$LOGFILE"

service barx stop
echo "ApplicationStop completed." >> "$LOGFILE"