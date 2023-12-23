#!/bin/bash

cd /opt/vdi-panel


if which docker > /dev/null 2>&1; then

    docker compose exec vdi-panel sh -c "python vdiManager/manage.py  timeupdate"

else
    echo "docker command does not exist."
    exit 1
fi