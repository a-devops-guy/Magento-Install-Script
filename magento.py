import os
from dotenv import load_dotenv
from pathlib import Path
import re

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# os.system("apt-get update -y & \
#     apt-get upgrade -y")

with open("/etc/os-release") as f:
    d = {}
    for line in f:
        k,v = line.rstrip().split("=")
        d[k] = v.strip('"')

fossa = re.findall("^20", d["VERSION_ID"])
bionic =  re.findall("^18", d["VERSION_ID"])
mage_24 = re.findall("^2.4", os.getenv("MAGENTO_VERSION"))
mage_23 = re.findall("^2.3", os.getenv("MAGENTO_VERSION"))

if mage_24 and d["ID"] == "ubuntu" and fossa:
    os.system("apt -y install software-properties-common & \
        add-apt-repository ppa:ondrej/php & \
        apt-get update -y & \
        apt -y install php7.4 php7.4-fpm php7.4-{bcmath,ctype,curl,dom,gd,iconv,intl,mbstring,mysql,simplexml,soap,xsl,zip,sockets}")
    os.system("apt -y install apache2 & \
        systemctl stop apache2 & \
        systemctl disable apache2")
    os.system("apt -y install nginx & \
        systemctl start nginx & \
        systemctl enable nginx")
    os.system("""php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" & \
        php composer-setup.php""")
    os.system("apt -y install mysql-server & \
        systemctl start mysql-server & \
        systemctl enable mysql-server")

elif mage_23 and d["ID"] == "ubuntu" and bionic:
    os.system("apt -y install software-properties-common & \
        add-apt-repository ppa:ondrej/php & \
        apt-get update -y & \
        apt -y install php7.3 php7.3-fpm php7.43-{bcmath,ctype,curl,dom,gd,iconv,intl,mbstring,mysql,simplexml,soap,xsl,zip,sockets}")
    os.system("apt -y install apache2 & \
        systemctl stop apache2 & \
        systemctl disable apache2")
    os.system("apt -y install nginx & \
        systemctl stop nginx & \
        systemctl enable nginx")
    os.system("""php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" & \
        php composer-setup.php --version=1.10.17""")

elif mage_24 and d["ID"] == "ubuntu" and bionic:
    print("Due to dependency limitation Magento 2.4 works only on Ubuntu v20")

elif mage_23 and d["ID"] == "ubuntu" and fossa:
    print("Due to dependency limitation Magento 2.3 works only on Ubuntu v18")

else:
    print("Your OS is Unsupported as this script works only with ubuntu")
    exit()