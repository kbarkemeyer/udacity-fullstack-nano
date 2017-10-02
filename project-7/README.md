# Linux Server Configuration

### [Full Stack Web Developer Nanodegree](https://classroom.udacity.com/nanodegrees/nd004/syllabus) (Project 7)
#### By Karen Barkemeyer ####

## Overview
The objective of this project is to take a baseline installation of a Linux server and prepare it to host a web applications. This involves securing the server from a number of attack vectors, install and configure a database server, and deploy Fullstack project-5 onto it.

## Server details:

Static IP address: 34.214.247.249

DNS name: karenbarkemeyer.com

SSH port: 2200

Webserver port: 443

## Securing the server:

1. Updata all currently installed packages:

` sudo apt-get update `

` sudo apt-get upgrade `

2. Change SSH port from 22 to 2200:

Open sshd_config file with command:

` sudo nano /etc/ssh/sshd_config `

Change SSH port to 2200 and save file.

In the networking tab on Lightsail webside add custom firewall rule for port 2200.

3. Configure Uncomplicated Firewall (UFW) to only allow incoming connections for SSH (port 2200), HTTP (port 80), and NTP (port 123).

` sudo ufw default deny incoming `

` sudo ufw default allow outgoing `
` sudo ufw allow 2200/tcp `

` sudo ufw allow www `

` sudo ufw allow ntp `

To confirm that correct setting have been added check with:

` sudo ufw show added `

` sudo ufw enable `

To check if firewall working correctly check:

` sudo ufw status `

Source:
Udacity Full Stack Nano Degree [https://classroom.udacity.com/nanodegrees/nd004/syllabus/core-curriculum]

## Give 'grader' access

1. Create a new user called 'grader'.
` sudo useradd -m -s /bin/bash grader `

2. Give 'grader' sudo privileges.
` sudo usermod -aG sudo grader `

3. On your LOCAL machine create a pair of SSH keys with ` ssh-keygen `. Copy public key.
On your your server change to user to grader with ` su - grader `. Create ssh directory with ` mkdir .ssh `. Create a new file with ` sudo nano .ssh/authorized_keys ` and paste public key into it. Save.

Change file permissions:

` chmod 700 .ssh `

` chmod 644 .ssh/authorized_keys `

4. Open sshd_config file with ` sudo nano /etc/ssh/sshd_config `. To **disable root login** change PermitRootLogin to no, to **inforce key-based authentication** change PasswordAuthentication to no. Save. Restart ssh with ` sudo service ssh restart `.

Sources:
Udacity Full Stack Nano Degree [https://classroom.udacity.com/nanodegrees/nd004/syllabus/core-curriculum]

DigitalOcean [https://www.digitalocean.com/community/tutorials/how-to-create-a-sudo-user-on-ubuntu-quickstart]

## Prepare server to deploy catalog app

### Set timezon to UTC

Check timezone with ` date `. If not UTC change to UTC with ` sudo timedatectl set-timezone UTC `. 

Source:
Askubuntu [https://askubuntu.com]

### Install Apache

Install Apache to serve Python mod-wsgi application
` sudo apt-get install apache2 `
` sudo apt-get install libapache2-mod-wsgi `

### Install PostgreSQL

1. Install PostgesSQL and create *catalog* user with limited permission
` sudo apt-get install postgresql postgresql-contrib ` 

2. Make sure remote connections are not allowed (default when first installing postgresql)
` sudo nano /etc/postgresql/9.5/main/pg_hba.conf `

File should look like this:

``` 
local   all             postgres                                peer 
local   all             all                                     peer 
host    all             all             127.0.0.1/32            md5 
host    all             all             ::1/128                 md5 
```

3. Postgres has automatically created a  Linux user called *postgres*. Change to this user with ` sudo su - postgres `. To run PostgreSQL interactive terminal program type ` psql `.

4. Create a new user named 'catalog' with: ` CREATE USER catalog WITH PASSWORD 'yourpassword'; `

5. Create a 'catalog' database with: ` CREATE DATABASE catalog WITH OWNER catalog; ` and connect to it with: ` \c catalog `.

6. Revoke all rights in this database from public: REVOKE ALL ON SCHEMA public FROM public; `

7. Give role/user 'catalog' permission to create tables: ` # GRANT ALL ON SCHEMA public TO catalog; ` 

8. Make sure to log out of PostgreSQL and change user back to grader with: ` \q ` then ` exit `.

Sources:
DigitalOcean [https://www.digitalocean.com/community/tutorials/how-to-secure-postgresql-on-an-ubuntu-vps]
ubuntu [https://help.ubuntu.com/community/PostgreSQL]


### Install git and clone repo

1. Install git
` sudo apt-get install git `
` git config --global user.name "username" `
` git config --global user.email useremail `

2. Move to /var/www with: ` cd /var/www `

3. Clone repo from github: ` git clone https://github.com/kbarkemeyer/udacity-fullstack-nano.git udacity-fullstack-nano `

4. Rename project-5 to FlaskApp: ` sudo mv project-5 FlaskApp `

5. In FlaskApp rename *item-catalog_app.py* to *_init__.py*

6. In *_init_.py* and *item_catalog_db.py* change *engine* to ` create_engine('postgresql://catalog:YOURPASSWORD@localhost/catalog') `

[The .git folder will be inaccessible from the web automatically. The only directory that can be listed in the browser is the static folder.]


### Create WSGI file

1. In the udacity-fullstack-nano directory create a wsgi file with: `sudo nano flaskapp.wsgi ` with the following content:

``` 
	import sys
	import logging
	logging.basicConfig(stream=sys.stderr)
	sys.path.insert(0, "/var/www/udacity-fullstack-nano/")

	from FlaskApp import app as application
	application.secret_key = 'secretkey'

```
Source:
DigitalOcean [https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps]

### Create virtual host config file

1. ` sudo nano /etc/apache2/sites-available/FlaskApp.conf `

    and add the following code:
```
<VirtualHost *:80>
    ServerName 34.214.109.139
    ServerAlias ec2-34-214-109-139.us-west-2.compute.amazonaws.com
    ServerAdmin admin@34.214.109.139
    WSGIScriptAlias / /var/www/udacity-fullstack-nano/flaskapp.wsgi
    <Directory /var/www/udacity-fullstack-nano/FlaskApp/>
            Order allow,deny
            Allow from all
    </Directory>
    Alias /static /var/www/udacity-fullstack-nano/FlaskApp/static
    <Directory /var/www/udacity-fullstack-nano/FlaskApp/static/>
            Order allow,deny
            Allow from all
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
 ```
2. Enable virtual host:
   ` sudo a2ensite FlaskApp `

3. Reload apache:
   ` service apache2 reload `

Source:
DigitalOcean [https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps]


### If you decide to use a virtual environment, install virtual environment with pip:

1. ` sudo apt-get install python-pip `

2. ` sudo pip install virtualenv `

3. Move to */var/www/udacity-fullstack-nano/FlaskApp* and create virtual environment with ` sudo virtualenv venv `. 

4. Activate virtual environment: ` source venv/bin/activate `.

5. Change permissions on virtual environment folder: ` sudo chmod -R 777 venv `

6. Install Flask: ` pip install Flask `.

7. Install other dependencies: ` pip install sqlalchemy psycopg2 `

8. Install pycurl: ` sudo apt-get install libssl-dev libcurl4-openssl-dev python-dev ` then ` pip install pycurl `.

9. Add the following lines to the top of your .wsgi file:

``` 
activate_this = '/var/www/udacity-fullstack-nano/FlaskApp/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this)) 
```

This will activate your virtual environment.

If not working with a virtual environment, just install the same dependencies globally.

10. Run *item_catalog_db.py* to set up database.

Sources:
Flask [http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/]

DigitalOcean [https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps]


### Setting up secure login with Amazon/ Securing your webpage

1. Register as a developer with Amazon and retrieve your client_id and client_secret. Save both as a JSON object "a", under the file name 'amazon_client_id_secret.json' in the same folder as your app, like so:
{
  "a": {
    "client_id": "YOUR_AMAZON_CLIENT_ID",
    "client_secret": "YOUR_AMAZON_CLIENT_SECRET"
  }
}

2. In the Amazon developer console whitelist your domain.

3. In the bookappLogin template enter your client id in line nine and your domain name in line 43.

4. Amazon login requires the https protocol for allowed origins. The easy way to fulfill this requirement fo testing is to create a self-signed SSL certificate via OpenSSl on Ubuntu.

First create a ssl directory:
` mkdir /etc/apache2/ssl `

Then generate the SSL with openssl:

` openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/apache2/ssl/apache.key -out /etc/apache2/ssl/apache.crt `

This will create an output with question to answer. Answer the questions appropriately and most importantly enter your fully qualified domain name (FQDN).

Now you can enter the self-signed SSL certificate to Apache.
` sudo nano /etc/apache2/sites-available/default-ssl.conf `
Find ` VirtualHost _default_:443 ` then ` ServerAdmin webmaster@localhost ` and add your virtual host configuration on the next line:
` ServerName YOURFULLYQUALIFIEDDOMAINNAME.com:443 ` and replace YOURFULLYQUALIFIEDDOMAINNAME with your domain name (as specified in common name prior).
Make sure the virtual host contains the following variables:

``` 
SSLEngine on
SSLCertificateFile /etc/apache2/ssl/apache.crt
SSLCertificateKeyFile /etc/apache2/ssl/apache.key 
```

Activate virtual host:
` a2ensite default-ssl `

Open firewall for port 443:
`sudo ufw allow 443 ` and on the lightsail console

Restart Apache:
` service apache2 restart `

Now you can visit your domain via https. Your webbrowser will give you a warning because self-signed SSL certificates are nor verifiable by a third=party certificate provider. This is for testing only. The amazonaws domain is not certifiable via third party!

Source:
Liquid Web [https://www.liquidweb.com/kb/how-to-create-a-self-signed-ssl-certificate-on-ubuntu/]

# Extra

## Pointing your Lightsail instance to your domain name and securing your domain

If you have registered a domain name, you can point your Lightsail instance to this domain. 

1. Go to your Lighsail instance and create a static IP address as described here [https://lightsail.aws.amazon.com/ls/docs/how-to/article/lightsail-create-static-ip].

2. Creata a DNS zone your Lightsail instance homepage, by choosing *Create DNS zone*. Click *Add record*  and create for example an A record. Enter your domain name. Your instance IP address will have been automatically entered. Save.

3. Go to your domain name service (for example Amazon Route 53). Create a hosted zone and add the resource record set as decribed here [http://docs.aws.amazon.com/Route53/latest/DeveloperGuide/CreatingNewSubdomain.html#AddNewSubdomainRecords].

Now you are ready to secure your domain. *Let's Encrypt* provides a free service to do that.

4. The official Let's Encrypt client to fetch the certificates is Certbot. We need to add the appropriate repositary:
` sudo add-apt-repository ppa:certbot/certbot `

ENTER, then update package information:
` sudo apt-get update `

Install Certbot:
` sudo apt-get install python-certbot-apache `

Obtain certificate:
` sudo certbot --apache -d example.com ` (replace example.com with your domain name)
You will be presented with a guide to set up different certificate options and asked to provide and email address. 

Optional:
Let's Encrypt's certificates are valid for 90 days. You might want to set up autorenewal as a cron job:
Type ` sudo crontab -e ` to open the default crontab. Paste in the following at the end of the file to run renewal check daily at 3:15: ` 15 3 * * * /usr/bin/certbot renew --quiet `. Save and close.

When installation is finished certbot will have created a new config file in the following location: /etc/apache2/sites-available. In this case FlaskApp-le-ssl.conf. Find your conf file and make sure it contains the correct ServerName SSLCertificateFile and SSLCertificateKeyFile variables. 

You can access your webpage now with https!

Source: 
DigitalOcean [https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-ubuntu-16-04]
