#!/bin/bash

cd vdiManager

python manage.py makemigrations && python manage.py migrate

python manage.py registerlicense -d $DJANGO_LICENSE_DAYS -p $DJANGO_LICENSE_USERS -a $DJANGO_LICENSE_API -N $DJANGO_LICENSE_FULL_NAME -n $DJANGO_LICENSE_SHORT_NAME

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (python manage.py createsuperuser --username=$DJANGO_SUPERUSER_USERNAME --email=$DJANGO_SUPERUSER_EMAIL --noinput)
fi

(gunicorn -c vdiManager/gunicorn_conf.py) &

nginx -g "daemon off;"