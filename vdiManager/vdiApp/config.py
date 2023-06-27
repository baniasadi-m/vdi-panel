from os import environ
class Config:
    DOCKER_DESKTOP_IMAGE = environ.get('VD_DESKTOP_IMAGE','dorowu/ubuntu-desktop-lxde-vnc')
    DOCKER_BROWSER_IMAGE = environ.get('VD_BROWSER_IMAGE','filebrowser/filebrowser')
