#!/bin/bash

apt-get update -y
apt-get upgrade -y

source /etc/os-release
if [ $ID = "ubuntu" ] && [ $VERSION_ID = 20.03 ]; then
    echo "Strings are equal."
else
    echo "Strings are not equal."
fi

echo "Your OS is $ID $VERSION_ID"
#cat /etc/os-release | grep 'ID='
#cat /etc/os-release | grep 'VERSION_ID='

future 
es version select
add php config edit - sed
add left over magento env from website 
