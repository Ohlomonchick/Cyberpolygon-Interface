#!/bin/bash
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
