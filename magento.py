import os
from dotenv import load_dotenv
from pathlib import Path
import re
from goto import goto, label

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

def common_package():
    os.system("apt -y install software-properties-common & \
        add-apt-repository ppa:ondrej/php & \
        apt-get update -y")
    os.system("apt -y install apache2 & \
        systemctl stop apache2 & \
        systemctl disable apache2")
    os.system("apt -y install nginx & \
        systemctl start nginx & \
        systemctl enable nginx")
    os.system("""php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');""")

def magento_compose():
    command = "cd %s & \
        composer create-project --repository-url=https://repo.magento.com/ magento/project-community-edition=%s magento" % (os.getenv('MAGENTO_VERSION',default="2.4.1"),os.getenv('MAGENTO_LOCATION',default="/var/www/"))
    os.system(command)
    os.system("chown :www-data -R magento & \
        cd magento & \
        find var generated vendor pub/static pub/media app/etc -type f -exec chmod u+w {} + & \
        find var generated vendor pub/static pub/media app/etc -type d -exec chmod u+w {} + & \
        chmod u+x bin/magento")

def sample_data():
    command = "cd %s" % (os.getenv('MAGENTO_LOCATION',default="/var/www/"))
    os.system(command)
    os.system("cd magento & \
        php bin/magento sampledata:deploy")

def nginx_config(vphp):
    command = "cp ./nginx.conf /etc/nginx/magento.conf"
    os.system(command)
    command = "sed -i 's|server  unix:/run/php-fpm/php-fpm.sock;|server  unix:/run/php-fpm/%s-fpm.sock;|g' & \
        sed -i 's|listen 80;|listen %d;|g' & \
        sed -i 's|server_name www.magento-dev.com;|server_name %s|g' & \
        sed -i 's|set $MAGE_ROOT /usr/share/nginx/html/magento;|set $MAGE_ROOT %smagento|g' & \
        sed -i 's|include /usr/share/nginx/html/magento/nginx.conf.sample;|include %smagento/nginx.conf.sample;|g' & \
        rm -f /etc/nginx/site-enabled/default.conf & \
        ln -s /etc/nginx/site-available/magento.conf /etc/nginx/site-enabled/ & \
        systemctl restart nginx" % (vphp,os.getenv('MAGENTO_PORT',default="80"),os.getenv('MAGENTO_PORT',default="www.magento-dev.com"),os.getenv('MAGENTO_LOCATION',default="/var/www/"),os.getenv('MAGENTO_LOCATION',default="/var/www/"))
    os.system(command)

def mage_install():
    print()

os.system("apt-get update -y & \
    apt-get upgrade -y")

with open("/etc/os-release") as f:
    d = {}
    for line in f:
        k,v = line.rstrip().split("=")
        d[k] = v.strip('"')

fossa = re.findall("^20", d["VERSION_ID"])
bionic =  re.findall("^18", d["VERSION_ID"])
mage_24 = re.findall("^2.4", os.getenv("MAGENTO_VERSION"))
mage_23 = re.findall("^2.3", os.getenv("MAGENTO_VERSION"))

label .start_mysql
print("WARNING: magento 2.3 support only 5.7 and magento 2.4 support only mysql 8.0")
Input = input("do you want mysql to be installed locally (y/n)?").lower().strip()
if Input[0] == 'y':
    os.system("apt -y install mysql-server & \
    systemctl start mysql-server & \
    systemctl enable mysql-server")
    DB_HOST="127.0.0.1"
    DB_NAME="magento"
    DB_USER="magento"
    DB_PASSWORD="Magento@321"
elif Input[0] == 'n':
    print("Using varibles from .env files for installation")
    print("DB HOST: ", os.getenv('DB_HOST'))
    print("DB NAME: ", os.getenv('DB_NAME'))
    print("DB USER: ", os.getenv('DB_USER'))
    print("DB PASSWORD: ", os.getenv('DB_PASSWORD'))
    print("DB TABLE PREFIX: ", os.getenv('DB_PREFIX',default=""))
    DB_HOST=os.getenv('DB_HOST')
    DB_NAME=os.getenv('DB_NAME')
    DB_USER=os.getenv('DB_USER')
    DB_PASSWORD=os.getenv('DB_PASSWORD')
    DB_PREFIX=os.getenv('DB_PREFIX',default="")
else:
    print("Invalid input. Please enter y or n")
    goto .start_mysql

label .start_es
Input = input("do you want elasticsearch to be installed locally (y/n)?").lower().strip()
if Input[0] == 'y':
    os.system("""wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add - & \
    apt-get install apt-transport-https && apt-get install openjdk-11-jre -y & \
    echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-7.x.list & \
    apt-get update -y && apt-get install elasticsearch -y""")
    SEARCH_ENGINE="elasticsearch7"
    ELASTICSEARCH_HOST="127.0.0.1"
    ELASTICSEARCH_PORT=9200
    ELASTICSEARCH_INDEX_PREFIX=""
    ELASTICSEARCH_TIMEOUT=60
    ELASTICSEARCH_ENABLE_AUTH=False
    ELASTICSEARCH_USERNAME=""
    ELASTICSEARCH_PASSWORD=""
elif Input[0] == 'n':
    print("Using varibles from .env files for installation")
    print("SEARCH ENGINE: ", os.getenv('SEARCH_ENGINE',default="elasticsearch7"))
    print("ELASTICSEARCH HOST: ", os.getenv('ELASTICSEARCH_HOST',default="127.0.0.1"))
    print("ELASTICSEARCH PORT: ", os.getenv('ELASTICSEARCH_PORT',default=9200))
    print("ELASTICSEARCH INDEX PREFIX: ", os.getenv('ELASTICSEARCH_INDEX_PREFIX',default=""))
    print("ELASTICSEARCH TIMEOUT: ", os.getenv('ELASTICSEARCH_TIMEOUT',default=""))
    print("ELASTICSEARCH ENABLE AUTH: ", os.getenv('ELASTICSEARCH_ENABLE_AUTH',default=""))
    print("ELASTICSEARCH USERNAME: ", os.getenv('ELASTICSEARCH_USERNAME',default=""))
    print("ELASTICSEARCH PASSWORD: ", os.getenv('ELASTICSEARCH_PASSWORD',default=""))
    SEARCH_ENGINE=os.getenv('SEARCH_ENGINE',default="elasticsearch7")
    ELASTICSEARCH_HOST=os.getenv('ELASTICSEARCH_HOST',default="127.0.0.1")
    ELASTICSEARCH_PORT=os.getenv('ELASTICSEARCH_PORT',default=9200)
    ELASTICSEARCH_INDEX_PREFIX=os.getenv('ELASTICSEARCH_INDEX_PREFIX',default="")
    ELASTICSEARCH_TIMEOUT=os.getenv('ELASTICSEARCH_TIMEOUT',default=60)
    ELASTICSEARCH_ENABLE_AUTH=os.getenv('ELASTICSEARCH_ENABLE_AUTH',default=False)
    ELASTICSEARCH_USERNAME=os.getenv('ELASTICSEARCH_USERNAME',default="")
    ELASTICSEARCH_PASSWORD=os.getenv('ELASTICSEARCH_PASSWORD',default="")
else:
    print("enter y or n")
    goto .start_es

label .start_redis
Input = input("do you want redis to be installed locally (y/n)?").lower().strip()
if Input[0] == 'y':
    os.system("apt -y install redis-server & \
    systemctl start redis-server & \
    systemctl enable redis-server")
elif Input[0] == 'n':
    print("Skipping redis installation")
else:
    print("enter y or n")
    goto .start_redis

if mage_24 and d["ID"] == "ubuntu" and fossa:
    common_package()
    os.system("apt -y install php7.4 php7.4-fpm php7.4-{bcmath,ctype,curl,dom,gd,iconv,intl,mbstring,mysql,simplexml,soap,xsl,zip,sockets}")
    os.system("php composer-setup.php")
    magento_compose()
    sample_data()
    nginx_config("php7.4")
    
elif mage_23 and d["ID"] == "ubuntu" and bionic:
    common_package()
    os.system("apt -y install php7.3 php7.3-fpm php7.3-{bcmath,ctype,curl,dom,gd,iconv,intl,mbstring,mysql,simplexml,soap,xsl,zip,sockets}")
    os.system("php composer-setup.php --version=1.10.17")
    magento_compose()
    sample_data()
    nginx_config("php7.3")
    
elif mage_24 and d["ID"] == "ubuntu" and bionic:
    print("Due to dependency limitation Magento 2.4 works only on Ubuntu v20")

elif mage_23 and d["ID"] == "ubuntu" and fossa:
    print("Due to dependency limitation Magento 2.3 works only on Ubuntu v18")

else:
    print("Your OS is Unsupported as this script works only with ubuntu")
    exit()