#!/bin/bash
export LOGFILE=/home/ec2-user/barx/deploylog
touch "$LOGFILE"

cat /home/ec2-user/barx/server/server.pid
echo "ValidateService completed." >> $LOGFILE
unset FOLDER
unset LOGFILE