#!/bin/bash
export PROD=True
export USE_POSTGRES=yes
export DB_HOST=192.168.100.5

sudo rm -rf /etc/nginx/sites-available/django_project
sudo cp nginx.conf /etc/nginx/sites-available/django_project
sudo chmod 444 /etc/nginx/sites-available/django_project
sudo chmod
sudo ln -sf /etc/nginx/sites-available/django_project /etc/nginx/sites-enabled
sudo systemctl restart nginx

gunicorn --workers 2 --bind 0.0.0.0:8001 Cyberpolygon.wsgi:application \
--access-logfile /var/log/syslog \
--error-logfile /var/log/syslog