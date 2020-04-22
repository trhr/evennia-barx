#!/bin/bash

export FOLDER=/home/ec2-user/barx

cd $FOLDER
service barx stop

if [ -d $FOLDER ]
then
  rm -rf $FOLDER
fi

mkdir -p $FOLDER

export LOGFILE=/home/ec2-user/barx/deploylog
touch $LOGFILE
echo "Starting install of barx" >> $LOGFILE