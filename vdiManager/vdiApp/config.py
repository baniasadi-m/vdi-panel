from os import environ
class Config:
    DOCKER_DESKTOP_IMAGE = environ.get('VD_DESKTOP_IMAGE','dorowu/ubuntu-desktop-lxde-vnc')
    DOCKER_BROWSER_IMAGE = environ.get('VD_BROWSER_IMAGE','filebrowser/filebrowser')
    Active_Directory_OUName = environ.get('VD_AD_OUName','AQRVdi')
    Active_Directory_DomainName = environ.get('VD_AD_DomainName','aqr.net')
    Active_Directory_ServerIP = environ.get('VD_AD_ServerIP','172.20.20.15')