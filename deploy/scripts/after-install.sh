#!/bin/bash

cp "/home/ec2-user/secrets/barx/secret_settings.py" "/home/ec2-user/barx/server/conf/secret_settings.py"
pip3 install -r /home/ec2-user/barx/requirements.txt

export LOGFILE=/home/ec2-user/barx/deploylog
touch "$LOGFILE"
echo "AfterInstall completed." >> "$LOGFILE"