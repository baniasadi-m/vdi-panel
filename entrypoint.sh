#!/bin/bash

cd vdiManager

python manage.py makemigrations && python manage.py migrate

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (python manage.py createsuperuser --username=$DJANGO_SUPERUSER_USERNAME --email=$DJANGO_SUPERUSER_EMAIL --noinput)
fi

(gunicorn -c vdiManager/gunicorn_conf.py) &

nginx -g "daemon off;"