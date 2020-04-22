#!/bin/bash
export LOGFILE=/home/ec2-user/barx/deploylog
touch "$LOGFILE"

service barx start
echo "ApplicationStart completed." >> "$LOGFILE"