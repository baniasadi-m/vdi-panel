#!/bin/bash
########################################
#######  parsing args first  ###########
########################################

  while [ $# -gt 0 ];do
      arg1=$1
      case $arg1 in 
        -s)
	    siganl_compose=$2
            shift 2
            ;;
      esac
  done


###################################################
######## checking if command is installed #########
###################################################


if which docker > /dev/null 2>&1; then
    if [ $siganl_compose == 'up' ];then
        docker compose up -d --quiet-pull
    elif [ $siganl_compose == 'down' ];then
        docker compose down
    fi
else
    echo "docker command does not exist."
    exit 1
fi
