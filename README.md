# Magento Install Script

#### This script installs only magento v2 version not v1 
#### This script works only on ubuntu 18 & Ubuntu 20 OS

This script will install magento v2 on your ubuntu OS by inputting required details in .env file and start the script. The script will take care the rest starting from the mysql, ES & redis (if required) till the installation of the magento using setup:install 

#### WARNING: Due to dependency limitation Magento 2.4 works only on Ubuntu v20
#### WARNING: Due to dependency limitation Magento 2.3 works only on Ubuntu v18

#### How to run the script
1. Install the python requirements - python-dotenv or pip3 install -r requirements.txt

Recommended: use pip3 install -r requirements.txt as it install all dependencies if the list grows in future
2. Give all the required variabled in .env - refer magento doc for more info https://devdocs.magento.com/guides/v2.4/install-gde/install/cli/install-cli.html
3. Run the script - python3 magento.py
4. If the magento version in the .env and OS matches then the script will continue
5. After OS update script will prompt whether to install mysql,ES,redis locally or use the variables in the env file
6. Upon cofirmation the script will continue to install and open browser upon finish

#### Future Update
1. Use user preferred ES version if magento supports
2. Edit magento recommened PHP like nginx configuration
3. Support more os like centos
4. Change of module from OS to pexpect (https://github.com/pexpect/pexpect) & subprocess for more granular control of program flow 
5. User preference magento folder name
