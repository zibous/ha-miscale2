#!/bin/bash
#
# example: bash compile.sh -f mismartscale
#

# ----------------------------------------
# application = filename without extention
# ----------------------------------------
appname=""
file_name=""

# application folder
folder=${PWD}

## current used esphome
DOCKERIMAGE=esphome/esphome:2022.12.8

BuildApplication(){
    # ---------------------------------------
    # build the source filename
    # ---------------------------------------
    file_name="$appname.yaml"
    echo "Compile Application ${appname}, filename: ${file_name}"
    # build the application
    echo "Check persistant folders"
    mkdir -p ${folder}/{config/firmwares,cache} >/dev/null 2>&1
    # clean build for the application
    echo "Clean build for: ${file_name}"
    docker run --rm -v "${folder}/config":/config -v "${folder}/cache":/cache  -it ${DOCKERIMAGE} clean ${file_name}
    # build (compile) the application
    echo "Remove old firmware: ${folder}/config/firmwares/${appname}.bin"
    rm ${folder}/config/firmwares/${appname}.bin >/dev/null 2>&1
    echo "Compiling ${file_name}"
    docker run --rm -v "${folder}/config":/config -v "${folder}/cache":/cache -it ${DOCKERIMAGE} compile ${file_name}
    # get the application firmware
    echo "Get new firmware for ${appname}"
    cp ${folder}/config/build/${appname}/.pioenvs/${appname}/firmware.bin ${folder}/config/firmwares/${appname}.bin
    echo "Firmware ${appname} ready, filename: ${folder}/config/firmwares/${appname}.bin"
}

# ---------------------------------------
# main: check the arguments
# ---------------------------------------
while getopts ":f" option; do
  case $option in
    f)
      [[ -z "$2" ]] && { echo "Missing Filename!"; exit 1; }
      appname=$2
      BuildApplication
      exit 1
      ;;
    *)
      echo "Usage: $0 [-h help] [-f compile file w/o extention]"
      exit 1
      ;;
  esac
done
