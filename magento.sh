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
add elastic search & redis config
add left over magento env from website 
eecute script from any path
more os support (debian,redhat)- centos
change to subprocess for more control over program flow 

hostname 
if magento fodler exist delete the folder or skip or name change?
magento mysql db create (if db exist ask user for deletion or name change)