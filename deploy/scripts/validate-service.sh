#!/bin/bash
export LOGFILE=/home/ec2-user/barx/deploylog
touch "$LOGFILE"

if test -f "/home/ec2-user/barx/server/server.pid"; then
  echo "ValidateService completed." >> $LOGFILE
  exit 0
else
  echo "Could not ValidateService" >> $LOGFILE
  exit 1
fi

unset FOLDER
unset LOGFILE