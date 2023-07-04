FROM python:3.11-bullseye

ENV DJANGO_SUPERUSER_USERNAME ''
ENV DJANGO_SUPERUSER_PASSWORD ''
ENV DJANGO_SUPERUSER_EMAIL ''
ENV VDI_MYSQL_DB ''
ENV VDI_MYSQL_USER  ''
ENV VDI_MYSQL_PASSWORD ''
ENV VDI_MYSQL_HOST  ''
ENV VDI_MYSQL_PORT  ''
ENV VDI_DESKTOP_IMAGE ''
ENV VDI_BROWSER_IMAGE ''
ENV VDI_AD_OUName ''
ENV VDI_AD_DomainName ''
ENV VDI_AD_ServerIP ''
ENV VDI_GUNICORN_BIND ''
ENV VDI_ACCESS_LOG_DIR ''
ENV VDI_ERROR_LOG_DIR ''

# install nginx
RUN apt-get update && apt-get install nginx -y --no-install-recommends
COPY nginx_default.conf /etc/nginx/sites-enabled/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# copy source and install dependencies
WORKDIR /opt/app


RUN  pip install pip setuptools -U && pip install wheel  && \
     apt update && apt install -y --no-install-recommends nano \
                                  iputils-ping pkg-config

COPY requirements.txt  .


RUN pip install -r requirements.txt

COPY . .

RUN chown -R www-data:www-data /opt/app


# start server
EXPOSE 80
STOPSIGNAL SIGTERM
CMD ["/opt/app/entrypoint.sh"]