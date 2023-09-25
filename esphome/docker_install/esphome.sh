
#!/bin/bash

# ---------------------------------------------
# sudo bash esphome.sh
# see: https://hub.docker.com/r/esphome/esphome
# ----------------------------------------------

IDu=$(id -u) # UID
IDg=$(id -g) # GID

CURRENTURL=http://$(hostname).$(dnsdomainname)
DOCKER_TIMEZONE=Europe/Berlin
DOCKERIMAGE=esphome/esphome:dev
CONTAINERLABEL=esphome
APPSDATA=$PWD${DOCKER_APPSDIR}${CONTAINERLABEL}

# create peristant folders
mkdir -p ${APPSDATA}/{config,firmwares,cache} >/dev/null 2>&1

echo "Try to remove previuos installation ${CONTAINERLABEL}..."
docker stop ${DOCKERIMAGE} && docker rm ${DOCKERIMAGE}

echo "Install Docker container ${CONTAINERLABEL}."
docker run --detach --interactive\
  --name ${CONTAINERLABEL}\
  --publish "6052:6052"\
  --privileged=true\
  --env TZ=${DOCKER_TIMEZONE}\
  --restart unless-stopped\
  --volume /run/udev:/run/udev\
  --volume /etc/localtime:/etc/localtime:ro\
  --volume ${APPSDATA}/config:/config\
  --volume ${APPSDATA}/cache:/cache\
  --network host \
  ${DOCKERIMAGE}

echo "Docker container ${CONTAINERLABEL} ready."
echo "Run WEBGUI: ${CURRENTURL}:6052"
