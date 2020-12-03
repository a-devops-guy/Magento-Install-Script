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
    print("magento 2.4")
    os.system("apt -y install software-properties-common & \
        add-apt-repository ppa:ondrej/php & \
        apt-get update -y & \
        apt -y install php7.4 php7.4-fpm")

elif mage_23 and d["ID"] == "ubuntu" and bionic:
    print("magento 2.3")
    
else:
    print("Due to dependency limitation Magento 2.3 works with Ubuntu 18 and Magento 2.4 works with Ubuntu 20")
    print("Unsupported OS script works only with ubuntu")
    exit()

    #test