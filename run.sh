#!/bin/bash 

if which docker > /dev/null 2>&1; then
    docker compose up -d --quiet-pull
else
    echo "docker command does not exist."
    exit 1
fi

