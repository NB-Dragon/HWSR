#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

FILE=GoogleNet_HCCR.caffemodel
CHECKSUM=cf2bcce4a3d0338559b8e5e6d5b5a4fe

if [ -f $FILE ]; then
  echo "File already exists. Checking md5..."
  os=`uname -s`
  if [ "$os" = "Linux" ]; then
    checksum=`md5sum $FILE | awk '{ print $1 }'`
  elif [ "$os" = "Darwin" ]; then
    checksum=`cat $FILE | md5`
  fi
  if [ "$checksum" = "$CHECKSUM" ]; then
    echo "Model checksum is correct. No need to download."
    exit 0
  else
    echo "Model checksum is incorrect. Need to download again."
  fi
fi

echo "Downloading pre-trained googlenet_hccr models (39 MB)..."
wget https://raw.githubusercontent.com/chongyangtao/DeepHCCR/master/models/$(echo $FILE | tr '[A-Z]' '[a-z]')
mv $(echo $FILE | tr '[A-Z]' '[a-z]') $FILE
echo "Done. Please run this command again to verify that checksum = $CHECKSUM."
