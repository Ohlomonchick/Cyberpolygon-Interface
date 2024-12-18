#!/bin/bash
export PROD=True
export USE_POSTGRES=yes
export DB_HOST=192.168.100.5

sudo rm -rf /etc/nginx/sites-available/django_project
sudo cp nginx.conf /etc/nginx/sites-available/django_project
sudo chmod 444 /etc/nginx/sites-available/django_project
sudo ln -sf /etc/nginx/sites-available/django_project /etc/nginx/sites-enabled
sudo systemctl restart nginx

gunicorn Cyberpolygon.wsgi:application -c /mnt/c/Users/Dmitry/PycharmProjects/Cyberpolygon/gunicorn.conf.py
