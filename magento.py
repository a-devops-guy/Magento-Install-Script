import os
from dotenv import load_dotenv
from pathlib import Path
import re
import shlex
import subprocess
import pymysql

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
script_path = os.getcwd()

def common_package():
    os.system("apt -y install software-properties-common & \
        add-apt-repository ppa:ondrej/php & \
        apt-get update -y & \
        apt-get install -y unzip")
    os.system("apt -y install apache2 & \
        systemctl stop apache2 & \
        systemctl disable apache2")
    os.system("apt -y install nginx & \
        systemctl start nginx & \
        systemctl enable nginx")
    os.system(""""php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');""""")
    os.system("php composer-setup.php --install-dir=/usr/local/bin --filename=composer")
    os.system("composer -n self-update 1.10.17")

def magento_compose():
    command = "composer config -g -n http-basic.repo.magento.com %s %s & \
         composer -n create-project --repository-url=https://repo.magento.com/ magento/project-community-edition=%s %s/magento" % (os.getenv('ACCESS_KEY'),os.getenv('SECRET_KEY'),os.getenv('MAGENTO_VERSION'),os.getenv('MAGENTO_LOCATION'))
    os.system(command)
    os.chdir(os.getenv('MAGENTO_LOCATION'))
    os.system("chown :www-data -R magento")
    os.chdir('magento')
    os.system("find var generated vendor pub/static pub/media app/etc -type f -exec chmod u+w {} + & \
        find var generated vendor pub/static pub/media app/etc -type d -exec chmod u+w {} + & \
        chmod u+x bin/magento")

def sample_data(q):
    Input = input(q + ' (y/n): ').lower().strip()
    if Input[0] == 'y':
        os.chdir(os.getenv('MAGENTO_LOCATION'))
        os.chdir('magento')
        os.system("php bin/magento sampledata:deploy")
    elif Input[0] == 'n':
        print("skipping sample data")
    else:
        print("enter y or n")
        return sample_data("please enter y/n")

def nginx_config(vphp):
    os.chdir(script_path)
    command = "cp -f ./nginx.conf /etc/nginx/sites-available/magento.conf"
    os.system(command)
    os.chdir('/etc/nginx/sites-available/')
    
    nginx_default = Path("/etc/nginx/sites-enabled/default.conf")
    if nginx_default.is_file():
        os.system("rm -f /etc/nginx/sites-enabled/default.conf")
    
    command = "sed -i 's|server  unix:/run/php-fpm/php-fpm.sock;|server  unix:/run/php-fpm/%s-fpm.sock;|g' magento.conf & \
        sed -i 's|listen 80;|listen %s;|g' magento.conf & \
        sed -i 's|server_name www.magento-dev.com;|server_name %s;|g' magento.conf & \
        sed -i 's|set $MAGE_ROOT /usr/share/nginx/html/magento2;|set $MAGE_ROOT %s/magento;|g' magento.conf & \
        sed -i 's|include /usr/share/nginx/html/magento2/nginx.conf.sample;|include %s/magento/nginx.conf.sample;|g' magento.conf & \
        ln -sf /etc/nginx/sites-available/magento.conf /etc/nginx/sites-enabled/ & \
        systemctl restart nginx" % (vphp,os.getenv('MAGENTO_PORT'),os.getenv('MAGENTO_URL'),os.getenv('MAGENTO_LOCATION'),os.getenv('MAGENTO_LOCATION'))
    os.system(command)
    os.chdir(script_path)

def mage_install():
    os.chdir(os.getenv('MAGENTO_LOCATION'))
    os.chdir('magento')
    if os.getenv('MAGENTO_VERSION'):
        os.chdir(os.getenv('MAGENTO_LOCATION'))
        os.chdir('magento')
        command = """php bin/magento setup:install --admin-firstname=%s --admin-lastname=%s --admin-email=%s --admin-user=%s --admin-password=%s \
        --base-url=%s --backend-frontname=%s --db-host=%s --db-name=%s --db-user=%s --db-password=%s --db-prefix=%s --cleanup-database \
        --language=%s --currency=%s --timezone=%s --use-secure=%s --base-url-secure=%s --use-secure-admin=%s \
        --search-engine=%s --elasticsearch-host=%s --elasticsearch-port=%s --elasticsearch-index-prefix=%s --elasticsearch-timeout=%s --elasticsearch-enable-auth=%s --elasticsearch-username=%s --elasticsearch-password=%s """ % (os.getenv('ADMIN_FIRSTNAME'),os.getenv('ADMIN_LASTNAME'),os.getenv('ADMIN_EMAIL'),os.getenv('ADMIN_USER'),os.getenv('ADMIN_PASSWORD'),os.getenv('BASE_URL'),os.getenv('BACKEND_FRONTNAME'),DB_HOST,DB_NAME,DB_USER,DB_PASSWORD,DB_PREFIX,os.getenv('LANGUAGE'),os.getenv('CURRENCY'),os.getenv('TIMEZONE'),os.getenv('USE_SECURE'),os.getenv('BASE_URL_SECURE'),os.getenv('USE_SECURE_ADMIN'),SEARCH_ENGINE,ELASTICSEARCH_HOST,ELASTICSEARCH_PORT,ELASTICSEARCH_INDEX_PREFIX,ELASTICSEARCH_TIMEOUT,ELASTICSEARCH_ENABLE_AUTH,ELASTICSEARCH_USERNAME,ELASTICSEARCH_PASSWORD)
        os.system(command)
    else:
        os.chdir(os.getenv('MAGENTO_LOCATION'))
        os.chdir('magento')
        command = """php bin/magento setup:install --admin-firstname=%s --admin-lastname=%s --admin-email=%s --admin-user=%s --admin-password=%s \
        --base-url=%s --backend-frontname=%s --db-host=%s --db-name=%s --db-user=%s --db-password=%s --db-prefix=%s --cleanup-database \
        --language=%s --currency=%s --timezone=%s --use-secure=%s --base-url-secure=%s --use-secure-admin=%s""" % (os.getenv('ADMIN_FIRSTNAME'),os.getenv('ADMIN_LASTNAME'),os.getenv('ADMIN_EMAIL'),os.getenv('ADMIN_USER'),os.getenv('ADMIN_PASSWORD'),os.getenv('BASE_URL'),os.getenv('BACKEND_FRONTNAME'),DB_HOST,DB_NAME,DB_USER,DB_PASSWORD,DB_PREFIX,os.getenv('LANGUAGE'),os.getenv('CURRENCY'),os.getenv('TIMEZONE'),os.getenv('USE_SECURE'),os.getenv('BASE_URL_SECURE'),os.getenv('USE_SECURE_ADMIN'))
        os.system(command)

def mage_mysql(q):
    global DB_HOST,DB_NAME,DB_USER,DB_PASSWORD,DB_PREFIX
    print("WARNING: magento 2.3 support only 5.7 and magento 2.4 support only mysql 8.0")
    Input = input(q + ' (y/n): ').lower().strip()
    if Input[0] == 'y':
        os.system("apt -y install mysql-server & \
        systemctl start mysql & \
        systemctl enable mysql")
        DB_HOST="127.0.0.1"
        DB_NAME="magento"
        DB_USER="magento"
        DB_PASSWORD="Magento@321"
        DB_PREFIX=""
        print("DB HOST: ", DB_HOST)
        print("DB NAME: ", DB_NAME)
        print("DB USER: ", DB_USER)
        print("DB PASSWORD: ", DB_PASSWORD)
        query = """\"create user 'magento'@'localhost' identified by 'Magento@321$%'\""""
        command = "mysql -u root -e %s" % (query)
        os.system(command)
        query = """\"create database magento\""""
        command = "mysql -u root -e %s" % (query)
        os.system(command)
        query = """\"GRANT ALL PRIVILEGES ON magento.* TO 'magento'@'localhost'\""""
        command = "mysql -u root -e %s" % (query)
        os.system(command)
    elif Input[0] == 'n':
        print("Using varibles from .env files for installation")
        print("DB HOST: ", os.getenv('DB_HOST'))
        print("DB NAME: ", os.getenv('DB_NAME'))
        print("DB USER: ", os.getenv('DB_USER'))
        print("DB PASSWORD: ", os.getenv('DB_PASSWORD'))
        print("DB TABLE PREFIX: ", os.getenv('DB_PREFIX'))
        DB_HOST=os.getenv('DB_HOST')
        DB_NAME=os.getenv('DB_NAME')
        DB_USER=os.getenv('DB_USER')
        DB_PASSWORD=os.getenv('DB_PASSWORD')
        DB_PREFIX=os.getenv('DB_PREFIX')
    else:
        print("Invalid input. Please enter y or n")
        return mage_mysql("please enter y/n")

def elasticsearch(q):
    if mage_23 and d["ID"] == "ubuntu" and bionic:
        return "no elaticsearch config required for magento 2.3. configure elasticsearch later in magento BO. skipping... "
    else:
        global SEARCH_ENGINE,ELASTICSEARCH_HOST,ELASTICSEARCH_PORT,ELASTICSEARCH_INDEX_PREFIX,ELASTICSEARCH_TIMEOUT,ELASTICSEARCH_ENABLE_AUTH,ELASTICSEARCH_USERNAME,ELASTICSEARCH_PASSWORD
        Input = input(q + " (y/n)?").lower().strip()
        if Input[0] == 'y':
            os.system("""wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add - & \
            apt-get install apt-transport-https && apt-get install openjdk-11-jre -y & \
            echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-7.x.list & \
            apt-get update -y && apt-get install elasticsearch -y & systemctl enable elasticsearch & systemctl start elasticsearch""")
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
            print("SEARCH ENGINE: ", os.getenv('SEARCH_ENGINE'))
            print("ELASTICSEARCH HOST: ", os.getenv('ELASTICSEARCH_HOST'))
            print("ELASTICSEARCH PORT: ", os.getenv('ELASTICSEARCH_PORT'))
            print("ELASTICSEARCH INDEX PREFIX: ", os.getenv('ELASTICSEARCH_INDEX_PREFIX'))
            print("ELASTICSEARCH TIMEOUT: ", os.getenv('ELASTICSEARCH_TIMEOUT'))
            print("ELASTICSEARCH ENABLE AUTH: ", os.getenv('ELASTICSEARCH_ENABLE_AUTH'))
            print("ELASTICSEARCH USERNAME: ", os.getenv('ELASTICSEARCH_USERNAME'))
            print("ELASTICSEARCH PASSWORD: ", os.getenv('ELASTICSEARCH_PASSWORD'))
            SEARCH_ENGINE=os.getenv('SEARCH_ENGINE')
            ELASTICSEARCH_HOST=os.getenv('ELASTICSEARCH_HOST')
            ELASTICSEARCH_PORT=os.getenv('ELASTICSEARCH_PORT')
            ELASTICSEARCH_INDEX_PREFIX=os.getenv('ELASTICSEARCH_INDEX_PREFIX')
            ELASTICSEARCH_TIMEOUT=os.getenv('ELASTICSEARCH_TIMEOUT')
            ELASTICSEARCH_ENABLE_AUTH=os.getenv('ELASTICSEARCH_ENABLE_AUTH')
            ELASTICSEARCH_USERNAME=os.getenv('ELASTICSEARCH_USERNAME')
            ELASTICSEARCH_PASSWORD=os.getenv('ELASTICSEARCH_PASSWORD')
        else:
            print("enter y or n")
            return elasticsearch("please enter y/n")

def redis(q):
    Input = input(q + " (y/n)?").lower().strip()
    if Input[0] == 'y':
        os.system("apt -y install redis-server & \
        systemctl start redis-server & \
        systemctl enable redis-server")
    elif Input[0] == 'n':
        print("Skipping redis installation")
    else:
        print("enter y or n")
        return redis("please enter y/n")

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

mage_mysql("\nDo you want to install mysql locally?")
elasticsearch("\nDo you want to install Elasticsearh locally?")
redis("\nDo you want to install redis locally?")

if mage_24 and d["ID"] == "ubuntu" and fossa:
    common_package()
    os.system("""apt -y install php7.4 php7.4-cli php7.4-fpm php7.4-bcmath php7.4-ctype php7.4-curl php7.4-dom php7.4-gd php7.4-iconv php7.4-intl php7.4-mbstring php7.4-mysql php7.4-simplexml php7.4-soap php7.4-xsl php7.4-zip php7.4-sockets""")
    magento_compose()
    sample_data("Do you want to install sample data?")
    nginx_config("php7.4")
    mage_install()
elif mage_23 and d["ID"] == "ubuntu" and bionic:
    common_package()
    os.system("""apt -y install php7.3 php7.3-cli php7.3-fpm php7.3-bcmath php7.3-ctype php7.3-curl php7.3-dom php7.3-gd php7.3-iconv php7.3-intl php7.3-mbstring php7.3-mysql php7.3-simplexml php7.3-soap php7.3-xsl php7.3-zip php7.3-sockets""")
    magento_compose()
    sample_data("Do you want to install sample data?")
    nginx_config("php7.3")
    mage_install()
elif mage_24 and d["ID"] == "ubuntu" and bionic:
    print("Due to dependency limitation Magento 2.4 works only on Ubuntu v20")
elif mage_23 and d["ID"] == "ubuntu" and fossa:
    print("Due to dependency limitation Magento 2.3 works only on Ubuntu v18")
else:
    print("Your OS is Unsupported as this script works only with ubuntu")
    exit()